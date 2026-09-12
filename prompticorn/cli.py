"""CLI module for prompt library management.

This module provides the command-line interface for managing AI assistant
configurations. It uses Click to define the CLI commands and orchestrates
the configuration, question handling, and output generation.

Commands:
    prompticorn init      - Interactive setup for AI assistant configurations
    prompticorn list      - Show all registered modes and their prompt files
    prompticorn validate  - Check for missing files and unregistered orphans
    prompticorn switch    - Switch between AI assistant tools
    prompticorn swap      - Swap active personas and regenerate configurations
    prompticorn update    - Update configuration options

Key Functions:
    - cli: Main Click group for the prompticorn CLI
    - list_prompts: Display all registered modes and their files
    - init_prompts: Interactive initialization workflow
    - update_command: Update configuration options
    - switch_command: Switch between AI tools
    - swap_command: Swap active personas
    - validate_prompts: Validate configuration integrity
"""

import sys
from pathlib import Path
from typing import Any

import click

from prompticorn.cli_utils import (
    get_supported_tools_display,
    normalize_tool_name,
    validate_tool_name,
)
from prompticorn.config_handler import (
    ConfigHandler,
)
from prompticorn.config_options import (
    CONFIG_OPTIONS,
    load_current_values,
    set_nested_value,
)
from prompticorn.console import configure_output_streams
from prompticorn.personas import PersonaRegistry
from prompticorn.questions.base.constants import RepositoryTypes
from prompticorn.questions.base.folder_spec import (
    FolderSpec,
    FolderSpecRegistry,
)
from prompticorn.questions.base.repository_type_question import RepositoryTypeQuestion
from prompticorn.questions.handlers.handle_single_language_questions import (
    resolve_answer,
    spec_key_for,
)
from prompticorn.questions.language import LANGUAGE_KEYS

# Legacy sweet_tea import removed - using Phase 2A builders
from prompticorn.tool_outputs import ToolOutputManager
from prompticorn.tools import menu_explanations as tool_menu_explanations
from prompticorn.tools import menu_options as tool_menu_options

# Bundled agents directory (same location prompt_builder discovers from)
# `validate` checks the on-disk *structure* of the bundled agents tree — a
# filesystem concern the resolver deliberately abstracts away, so it keeps a
# path. Content reads go through the resolver. (PRO-106)
_AGENTS_DIR = Path(__file__).parent / "agents"


def _content_exists(raw_unit_id: str) -> bool:
    """Whether the resolver carries a unit. Used by `list` to flag gaps. (PRO-106)"""
    from prompticorn.content.content_resolver import default_resolver
    from prompticorn.content.errors import InvalidUnitIdError
    from prompticorn.content.unit_id import UnitId

    try:
        return default_resolver().has(UnitId.parse(raw_unit_id))
    except InvalidUnitIdError:
        return False


def _digest_column(raw_unit_id: str) -> str:
    """Short content digest for `list`, or empty when the unit is absent. (PRO-108)

    Truncated for readability only — the full digest is what a lockfile pins.
    Absent content yields an empty string rather than a placeholder, so the
    ✗ MISSING marker stays the single signal for "not there".
    """
    from prompticorn.content.content_resolver import default_resolver
    from prompticorn.content.errors import ContentError
    from prompticorn.content.unit_id import UnitId

    try:
        digest = default_resolver().digest(UnitId.parse(raw_unit_id))
    except ContentError:
        return ""
    return f"  {click.style(digest[:_DIGEST_DISPLAY_LENGTH], dim=True)}"


# Enough hex to be unambiguous by eye without dominating the line.
_DIGEST_DISPLAY_LENGTH = 12


# Valid languages for each preset type/subtype


def _get_valid_languages(preset_type: str, subtype: str) -> list[str]:
    """Get valid languages for a preset type/subtype.

    Loads preset language mappings from YAML configuration file.

    Args:
        preset_type: The folder type (backend or frontend)
        subtype: The folder subtype

    Returns:
        List of valid language keys
    """

    import yaml

    from prompticorn.content.content_resolver import read_configuration

    preset_languages = yaml.safe_load(read_configuration("preset_languages"))

    if preset_type in preset_languages:
        if subtype in preset_languages[preset_type]:
            return preset_languages[preset_type][subtype]
    # Fallback to common languages if not found
    return ["python", "typescript", "javascript", "go", "java", "rust"]


def _setup_monorepo_folders() -> list[dict[str, Any]]:
    """Interactive setup for monorepo folder configuration.

    This function prompts the user to add folders to their monorepo,
    either through standard presets (frontend/backend) or custom paths.

    Returns:
        List of folder specifications.
    """
    import os

    from prompticorn.ui._selector import select_option_with_explain

    folder_specs: list[dict[str, Any]] = []
    add_more = True

    while add_more:
        # Removed: Headers not needed - select_option_with_explain clears screen
        # click.echo("\n" + "-" * 60)
        # click.secho("  Add Folder", bold=True)
        # click.echo("-" * 60)

        # Step 1: Ask for folder type (preset or custom)
        folder_type = select_option_with_explain(
            question="What type of folder would you like to add?",
            options=["backend (preset)", "frontend (preset)", "custom"],
            explanations={
                "backend (preset)": "Backend folder types: api, library, worker, cli, data",
                "frontend (preset)": "Frontend folder types: ui, library, e2e",
                "custom": "Define your own folder type and configuration",
            },
            question_explanation="Select a folder type: backend (api, library, worker, cli, data), frontend (ui, library, e2e), or custom",
            default_index=0,
            allow_multiple=False,
        )
        assert isinstance(folder_type, str), "allow_multiple=False should return str"

        # folder_type is str when allow_multiple=False
        if not isinstance(folder_type, str):
            click.secho("  Error: Expected single selection. Try again.", fg="red")
            continue

        if folder_type == "custom":
            # Custom folder: prompt for folder path
            os.system("clear" if os.name != "nt" else "cls")  # Clear screen after curses
            folder_path = click.prompt(
                "\nFolder path (e.g., services/auth/api)",
                default="",
            ).strip()

            if not folder_path:
                click.secho("  Folder path cannot be empty. Skipping.", fg="yellow")
                continue

            # Prompt for language
            os.system("clear" if os.name != "nt" else "cls")  # Clear screen
            language = click.prompt(
                "\nProgramming language",
                type=click.Choice(LANGUAGE_KEYS),
                default="python",
            )

            # Create custom folder spec
            spec = FolderSpec(
                folder=folder_path,
                type="custom",
                subtype="custom",
                language=language,
            )
            spec_dict = spec.to_dict()

            # Immediately ask language-specific questions for this folder
            spec_dict = _ask_language_questions_for_folder(spec_dict)

            folder_specs.append(spec_dict)
            click.echo(f"\n  Added: {folder_path} ({language})")

        else:
            # Preset: extract folder type
            preset_type = folder_type.split(" (")[0]  # "backend" or "frontend"

            # Get subtypes for this preset
            subtypes = list(FolderSpecRegistry.get_folder_type_presets()[preset_type].keys())
            subtype_options = [
                f"{s} ({FolderSpecRegistry.get_folder_type_presets()[preset_type][s]['language']})"
                for s in subtypes
            ]

            # Step 2: Ask for subtype
            subtype_choice = select_option_with_explain(
                question=f"What {preset_type} subtype?",
                options=subtype_options,
                explanations={
                    f"{s} ({FolderSpecRegistry.get_folder_type_presets()[preset_type][s]['language']})": f"{preset_type.capitalize()} {s} - uses {FolderSpecRegistry.get_folder_type_presets()[preset_type][s]['language']}"
                    for s in subtypes
                },
                question_explanation=f"Select the {preset_type} subtype to create",
                default_index=0,
                allow_multiple=False,
            )
            assert isinstance(subtype_choice, str), "allow_multiple=False should return str"
            # subtype_choice is str when allow_multiple=False
            subtype = subtype_choice.split(" (")[0]  # Extract subtype name

            # Step 3: Ask for folder path
            os.system("clear" if os.name != "nt" else "cls")  # Clear screen after curses
            folder_path = click.prompt(
                f"\nFolder path (e.g., {preset_type}/{subtype})",
                default=f"{preset_type}/{subtype}",
            ).strip()

            if not folder_path:
                folder_path = f"{preset_type}/{subtype}"

            # Get preset defaults
            preset_defaults = FolderSpecRegistry.get_folder_type_presets()[preset_type][subtype]
            default_language = preset_defaults["language"]

            # Step 4: Ask for language - filter to valid languages for this preset
            valid_languages = _get_valid_languages(preset_type, subtype)

            # Ensure default is in the list and at the front
            if default_language not in valid_languages:
                valid_languages.insert(0, default_language)

            language_choice = select_option_with_explain(
                question="Programming language?",
                options=valid_languages,
                explanations={
                    lang: f"Use {lang} for this {preset_type}/{subtype} folder"
                    for lang in valid_languages
                },
                question_explanation=f"Select language for {folder_path}. Default is {default_language} based on preset.",
                default_index=0,
                allow_multiple=False,
            )
            assert isinstance(language_choice, str), "allow_multiple=False should return str"
            # language_choice is str when allow_multiple=False
            language: str = language_choice

            # Create folder spec
            spec = FolderSpec(
                folder=folder_path,
                type=preset_type,
                subtype=subtype,
                language=language,
            )
            spec_dict = spec.to_dict()

            # Immediately ask language-specific questions for this folder
            spec_dict = _ask_language_questions_for_folder(spec_dict)

            folder_specs.append(spec_dict)
            click.echo(f"\n  Added: {folder_path} ({language})")

        # Step 4: Ask if more folders
        click.echo("\n")
        more = select_option_with_explain(
            question="Add another folder?",
            options=["Yes", "No"],
            explanations={
                "Yes": "Add another folder to the monorepo",
                "No": "Finish adding folders",
            },
            question_explanation="Choose whether to add more folders or finish setup",
            default_index=1,
            allow_multiple=False,
        )
        assert isinstance(more, str), "allow_multiple=False should return str"
        add_more = more == "Yes"

    return folder_specs


def _ask_language_questions_for_folder(spec: dict[str, Any]) -> dict[str, Any]:
    """Ask language-specific questions for a single folder.

    This function runs the language questionnaire for one folder spec,
    immediately after the folder is created (not in batch later).

    Args:
        spec: A single folder specification

    Returns:
        Updated folder specification with language-specific config

    Raises:
        QuestionPipelineError: If questions cannot be loaded for the language
    """
    from prompticorn.questions.language import (
        QuestionPipelineError,
        get_fungible_questions,
        get_language_questions,
    )
    from prompticorn.ui._selector import select_option_with_explain

    spec.get("folder", "")
    language = spec.get("language", "")

    if not language:
        return spec

    # Removed: headers before curses (gets cleared anyway)
    # click.echo("\n" + "-" * 60)
    # click.secho(f"  Configuring: {folder_path} ({language})", bold=True)
    # click.echo("-" * 60)

    # Get language-specific questions
    try:
        questions = get_language_questions(language)
    except QuestionPipelineError:
        # If no questions defined for this language, skip
        return spec

    # Ask each question
    for question in questions:
        answer = select_option_with_explain(
            question=question.question_text,
            options=question.options,
            explanations=question.option_explanations,
            question_explanation=question.explanation,
            default_index=0,
            allow_multiple=question.allow_multiple,
        )

        # Store the answer (resolving preset values like coverage targets)
        spec[spec_key_for(question, language)] = resolve_answer(question, answer)

    # Ask fungible (per-folder) questions keyed by this folder's type/subtype
    # (e.g. "backend/api"). These differ per workspace and surface the
    # context-aware framework questions defined in question_pipelines.yaml.
    fungible_type_key = f"{spec.get('type', '')}/{spec.get('subtype', '')}"
    try:
        fungible_questions = get_fungible_questions(language, fungible_type_key)
    except QuestionPipelineError:
        # If fungible questions cannot be loaded for this folder type, skip
        fungible_questions = []

    for question in fungible_questions:
        answer = select_option_with_explain(
            question=question.question_text,
            options=question.options,
            explanations=question.option_explanations,
            question_explanation=question.explanation,
            default_index=0,
            allow_multiple=question.allow_multiple,
        )

        # Store the answer (resolving preset values like coverage targets)
        spec[spec_key_for(question, language)] = resolve_answer(question, answer)

    return spec


def _ask_folder_questions(folder_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ask language-specific questions for each folder in the monorepo.

    This function iterates through each folder spec and asks the language-specific
    configuration questions (linter, test framework, etc.) defined in the question
    pipeline for that folder's language.

    Args:
        folder_specs: List of folder specifications from _setup_monorepo_folders

    Returns:
        Updated list of folder specifications with language-specific config

    Raises:
        QuestionPipelineError: If questions cannot be loaded for a language
    """
    from prompticorn.questions.language import get_language_questions
    from prompticorn.ui._selector import select_option_with_explain

    updated_specs: list[dict[str, Any]] = []

    for spec in folder_specs:
        spec.get("folder", "")
        language = spec.get("language", "")

        if not language:
            updated_specs.append(spec)
            continue

        # Removed: separator not needed before curses UI
        # click.echo("\n" + "-" * 60)
        # Removed: header before curses (gets cleared anyway)
        # click.secho(f"  Configuring: {folder_path} ({language})", bold=True)
        # Removed: separator not needed before curses UI
        # click.echo("-" * 60)

        # Get language-specific questions - this will raise if there are issues
        questions = get_language_questions(language)

        # Ask each question
        for question in questions:
            answer = select_option_with_explain(
                question=question.question_text,
                options=question.options,
                explanations=question.option_explanations,
                question_explanation=question.explanation,
                default_index=0,
                allow_multiple=question.allow_multiple,
            )

            # Store the answer (resolving preset values like coverage targets)
            spec[spec_key_for(question, language)] = resolve_answer(question, answer)

        updated_specs.append(spec)

    return updated_specs


def _ask_project_questions(select_option) -> dict[str, str]:
    """Ask project-level questions and return the config ``project`` section.

    Each project question's key is ``project_<field>``; the selected value is stored
    under ``<field>``. The "Not specified" option maps to an empty string.

    Args:
        select_option: Interactive selection function (select_option_with_explain).

    Returns:
        Dict of project settings (commit_style, pr_size, deploy_target). Note:
        layout_style and error_handling are now core per-language questions stored
        on each folder/spec, not project-level.
    """
    from prompticorn.questions.project import NOT_SPECIFIED, get_project_questions

    project: dict[str, str] = {}
    for question in get_project_questions():
        field = question.key.replace("project_", "")
        default_index = (
            question.options.index(question.default) if question.default in question.options else 0
        )
        value = select_option(
            question=question.question_text,
            options=question.options,
            explanations=question.option_explanations,
            question_explanation=question.explanation,
            default_index=default_index,
            allow_multiple=False,
        )
        project[field] = "" if value == NOT_SPECIFIED else str(value)
    return project


# # ── Initialize registry ───────────────────────────────────────────────────────
# fill_registry()


# ── Root group ─────────────────────────────────────────────────────────────────


@click.group()
def cli():
    """prompticorn CLI — manage and validate your prompt configurations.

    Edit files in prompts/, then use `prompticorn list` to see available modes and
    `prompticorn validate` to check configuration integrity.
    """
    # Before any command prints anything. The CLI's own output uses characters
    # cp1252 cannot encode, and a redirected stream on Windows would otherwise
    # abort a half-finished command while reporting what it had already done.
    configure_output_streams()


# ── list ───────────────────────────────────────────────────────────────────────


@cli.command("list")
def list_prompts():
    """
    List all discovered agents, their subagents, and prompt variants.

    Agents are discovered from the bundled agents directory. For each agent the
    base prompt.md is shown, and for each subagent the available minimal/verbose
    prompt variants. Files marked with ✓ exist on disk; ✗ MISSING are absent.

    Usage:
        prompticorn list
    """
    from prompticorn.agent_registry import Registry as AgentRegistry
    from prompticorn.agent_registry import RegistryLoadError

    try:
        reg = AgentRegistry.from_resolver()
    except RegistryLoadError as exc:
        click.secho(f"\n✗ Failed to load agent registry: {exc}", fg="red")
        sys.exit(1)

    click.echo("\n" + click.style("AGENT REGISTRY", bold=True))
    for name in reg.list_agents():
        agent = reg.get_agent(name)
        click.echo("\n" + click.style(name, bold=True) + f"  — {agent.description}")
        click.echo("  " + click.style(reg.artifact_id(name).render(), fg="cyan"))

        base_mark = "✓" if _content_exists(f"agent/{name}") else click.style("✗ MISSING", fg="red")
        click.echo(f"  {base_mark}  prompt.md{_digest_column(f'agent/{name}')}")

        subagents = reg.list_subagents(name)
        if subagents:
            click.echo("  subagents:")
            for sub in subagents:
                click.echo(f"    {sub}")
                click.echo(
                    "      " + click.style(reg.artifact_id(f"{name}/{sub}").render(), fg="cyan")
                )
                for variant in ("minimal", "verbose"):
                    unit = f"subagent/{name}/{sub}/{variant}"
                    vmark = "✓" if _content_exists(unit) else click.style("✗ MISSING", fg="red")
                    click.echo(f"      {vmark}  {variant}/prompt.md{_digest_column(unit)}")

    click.echo()


# ── init ───────────────────────────────────────────────────────────────────────


@cli.command("init")
def init_prompts():
    """
    Interactively initialize prompt configuration for your project.

    This is the main setup command that walks users through configuration:
    1. Select which AI assistant to configure (Kilo, Claude, Cline, Cursor, Copilot)
    2. Choose repository type (single-language or multi-language-monorepo)
    3. Select prompt variant (minimal for efficiency, verbose for detail)
    4. Choose active personas/roles (filters which agents are generated)
    5. Answer language-specific questions
     6. Clean up old artifacts if switching tools
    7. Generate configuration files for the selected AI tool

    Creates or updates .prompticorn.yaml with the configuration and
    generates tool-specific configuration files in appropriate directories.

    Usage:
        prompticorn init

    Interactive flow:
        ✓ Select AI tool
        ✓ Choose repository type
        ✓ Select prompt variant
        ✓ Select personas
        ✓ Answer language questions
        ✓ Configuration saved
        ✓ Tool configs generated
    """

    from prompticorn.ui._selector import select_option_with_explain
    from prompticorn.ui.exceptions import UserCancelledError

    # Removed: header stays in buffer when curses exits
    # click.echo("\n" + "=" * 60)
    # Removed: header stays in main buffer after curses exits, causes confusion
    # click.secho("  prompticorn Initialization", bold=True, fg="cyan")
    # Removed: header stays in buffer when curses exits
    # click.echo("=" * 60)
    # Removed: message stays in main buffer after curses exits
    # click.echo("\nUse up/down arrows, numbers, or Enter for defaults.")

    try:
        # Step 1: Select which AI assistant to configure
        ai_tool = select_option_with_explain(
            question="Which AI assistant would you like to configure?",
            options=tool_menu_options(),
            explanations=tool_menu_explanations(),
            question_explanation="Select one AI assistant to configure.",
            default_index=1,
            allow_multiple=False,
        )
        assert isinstance(ai_tool, str), "allow_multiple=False should return str"
        # Store the selected AI tool
        selected_tool: str = ai_tool

        # Step 2: Repository type
        # Removed: separator not needed before curses UI
        # click.echo("\n" + "-" * 60)
        repo_question = RepositoryTypeQuestion()
        default_idx = repo_question.options.index(repo_question.default)

        repo_type = select_option_with_explain(
            question=repo_question.question_text,
            options=repo_question.options,
            explanations=repo_question.option_explanations,
            question_explanation=repo_question.explanation,
            default_index=default_idx,
        )

        # Step 3: Ask for variant (minimal or verbose) - BEFORE language questions
        # Removed: separator not needed before curses UI
        # click.echo("\n" + "-" * 60)
        variant_question = select_option_with_explain(
            question="Which prompt variant would you like to use?",
            options=["Minimal", "Verbose"],
            explanations={
                "Minimal": "Lightweight prompts for faster tokens and lower costs",
                "Verbose": "Detailed prompts with more examples and explanations",
            },
            question_explanation="Choose between minimal (efficient) or verbose (detailed) prompts.",
            default_index=0,
            allow_multiple=False,
        )
        assert isinstance(variant_question, str), "allow_multiple=False should return str"
        variant = "minimal" if variant_question == "Minimal" else "verbose"

        # Step 3.5: Ask for personas
        # Removed: separator not needed before curses UI
        # click.echo("\n" + "-" * 60)
        try:
            from pathlib import Path

            from prompticorn.personas import PersonaRegistry

            # Load persona registry
            persona_registry = PersonaRegistry.from_resolver()

            # Build options and explanations for persona selection
            persona_ids = persona_registry.list_personas()
            persona_options = [persona_registry.get_display_name(pid) for pid in persona_ids]
            persona_explanations = {
                persona_registry.get_display_name(pid): persona_registry.get_description(pid)
                for pid in persona_ids
            }

            selected_personas_display = select_option_with_explain(
                question="Which personas will be working on this codebase?",
                options=persona_options,
                explanations=persona_explanations,
                question_explanation="Select one or more roles. Only agents/workflows for selected personas will be generated.",
                default_index=0,
                allow_multiple=True,
            )

            # Convert display names back to persona IDs
            if isinstance(selected_personas_display, list):
                display_to_id = {persona_registry.get_display_name(pid): pid for pid in persona_ids}
                selected_persona_ids = [
                    display_to_id[display_name] for display_name in selected_personas_display
                ]
            else:
                # Single selection (shouldn't happen with allow_multiple=True, but handle it)
                display_to_id = {persona_registry.get_display_name(pid): pid for pid in persona_ids}
                selected_persona_ids = [display_to_id[selected_personas_display]]

            # Store selected personas for later use
            active_personas = selected_persona_ids

        except Exception as e:
            # Fallback if persona loading fails - log warning and continue
            click.secho(
                f"  Warning: Could not load personas ({e}). Skipping persona selection.",
                fg="yellow",
            )
            active_personas = []  # Empty list = no filtering

        # Step 4: Handle language questions based on repo type
        # Use isinstance() for proper type narrowing from str | list[str] to str
        if isinstance(repo_type, str) and repo_type == RepositoryTypes.SINGLE:
            from prompticorn.questions.handlers.handle_single_language_questions import (
                HandleSingleLanguageQuestions,
            )

            handler = HandleSingleLanguageQuestions(select_option_with_explain)
            config: dict[str, Any] = handler.handle(repo_type)
            config["variant"] = variant  # Add variant to config
            config["active_personas"] = active_personas  # Add selected personas
        else:
            # Multi-folder or mixed - just save repo type for now
            if repo_type == RepositoryTypes.MULTI_MONOREPO:
                # Interactive folder setup for multi-language monorepo
                config = ConfigHandler.get_default_multi_language_template()
                config["repository"]["type"] = repo_type
                config["variant"] = variant  # Add variant to config
                config["active_personas"] = active_personas  # Add selected personas

                # Run interactive folder setup for multi-language monorepo
                # (language questions are now asked inline for each folder)
                folder_specs = _setup_monorepo_folders()

                config["spec"] = folder_specs

                # Create folders that don't exist
                if folder_specs:
                    click.echo("\n" + "-" * 60)
                    click.secho("  Creating folders...", bold=True)
                    click.echo("-" * 60)
                    for spec in folder_specs:
                        folder_path = Path(spec["folder"])  # type: ignore[reportPossiblyUnboundVariable]
                        if not folder_path.exists():
                            folder_path.mkdir(parents=True, exist_ok=True)
                            click.echo(f"  Created: {spec['folder']}")
                        else:
                            click.echo(f"  Exists: {spec['folder']}")
            else:
                # Mixed or other repo types - use default template
                config = ConfigHandler.get_default_single_language_template()
                config["repository"]["type"] = repo_type
                config["variant"] = variant  # Add variant to config
                config["active_personas"] = active_personas  # Add selected personas

        # Step 4.5: Ask project-level questions (database, ORM, commit style, etc.)
        try:
            config["project"] = _ask_project_questions(select_option_with_explain)
        except UserCancelledError:
            raise
        except Exception as e:
            click.secho(f"  Warning: Could not collect project settings ({e}).", fg="yellow")
            config.setdefault("project", ConfigHandler.get_default_project_settings())

        # Save configuration (now includes variant from Step 3)
        ConfigHandler.save_config(config)

        click.echo("\n\n" + "=" * 60)
        click.secho("  Configuration saved!", bold=True, fg="green")
        click.echo("=" * 60)
        click.echo(f"\n  Config file: {ConfigHandler.get_config_path()}")

        # Step 5: Clean up old artifacts if switching tools
        artifact_manager = ToolOutputManager()
        current_tool = artifact_manager.current_tool
        if selected_tool and current_tool and current_tool != selected_tool:
            click.echo("\n" + "-" * 60)
            click.secho("  Removing old artifacts...", bold=True)
            click.echo("-" * 60)
            removal_actions = artifact_manager.remove_outputs_created_by(current_tool)
            for action in removal_actions:
                click.echo(f"    {action}")

        # Step 6: Generate selected AI assistant configurations
        if selected_tool:
            click.echo("\n" + "-" * 60)
            click.secho(f"  Generating AI assistant configurations ({variant})...", bold=True)
            click.echo("-" * 60)

            output_path = Path(".")  # type: ignore[reportPossiblyUnboundVariable]
            normalized_tool = normalize_tool_name(selected_tool)
            builder = _get_builder(normalized_tool)
            if builder:
                actions = builder.build(output_path, config=config, dry_run=False)
                for action in actions:
                    click.echo(f"  {action}")
            else:
                click.secho(f"  ✗ Unknown tool: {selected_tool}", fg="yellow")

            click.echo("\n" + "=" * 60)
            click.secho("  Setup complete!", bold=True, fg="green")
            click.echo("=" * 60)

    except UserCancelledError:
        click.echo("\n\nOperation cancelled. No changes were saved.")
        raise click.Abort() from None

    click.echo()


# ══ switch ═══════════════════════════════════════════════════════════════════════


@cli.command("switch")
@click.argument("tool_name", required=False)
def switch_command(tool_name: str | None):
    """
    Switch to a different AI assistant tool.

    Allows changing which AI coding assistant to configure. Regenerates
    configurations for the selected tool using the existing .prompticorn.yaml
    configuration.

    The selected tool determines the output format and location:
    - Kilo Code IDE: .kilo/agents/ directory
    - Kilo Code CLI: .opencode/rules/ directory
    - Cline: .clinerules file
    - Cursor: .cursor/rules/ directory
    - GitHub Copilot: .github/copilot-instructions.md

    Args:
        tool_name: Name of the tool to switch to (optional; if not provided,
                  will prompt interactively for selection)

    Usage:
        prompticorn switch                  # Interactive menu
        prompticorn switch kilo-ide        # Switch directly to Kilo IDE
        prompticorn switch cline           # Switch directly to Cline
    """

    from prompticorn.ui._selector import select_option_with_explain
    from prompticorn.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'prompticorn init' first.",
            fg="red",
        )
        raise click.Abort()

    config = ConfigHandler.load_config()

    # Determine tool to switch to
    target_tool: str

    if tool_name is not None:
        # Normalize and validate the provided tool name
        normalized = normalize_tool_name(tool_name)
        if not validate_tool_name(normalized):
            click.secho(
                f"Error: Invalid tool '{tool_name}'. Supported tools: {get_supported_tools_display()}",
                fg="red",
            )
            raise click.Abort()
        target_tool = normalized
    else:
        # Show interactive menu
        try:
            target_tool_result = select_option_with_explain(
                question="Which AI assistant would you like to switch to?",
                options=tool_menu_options(),
                explanations=tool_menu_explanations(),
                question_explanation="Select an AI assistant to switch to.",
                default_index=1,
                allow_multiple=False,
            )
            assert isinstance(target_tool_result, str), "allow_multiple=False should return str"
            target_tool = target_tool_result
        except UserCancelledError:
            click.echo("\nOperation cancelled.")
            raise click.Abort() from None

    # Get current tool
    artifact_manager = ToolOutputManager()
    current_tool = artifact_manager.current_tool

    click.echo("\n" + "=" * 60)
    click.secho("  Switching AI Tool", bold=True, fg="cyan")
    click.echo("=" * 60)
    click.echo(f"\n  Current tool: {current_tool or 'none'}")
    click.echo(f"  Target tool:   {target_tool}")

    # Remove old artifacts if switching to a different tool
    if current_tool and current_tool != target_tool:
        click.echo("\n" + "-" * 60)
        click.secho("  Removing old artifacts...", bold=True)
        removal_actions = artifact_manager.remove_outputs_created_by(current_tool)
        for action in removal_actions:
            click.echo(f"    {action}")

    # Build new artifacts
    click.echo("\n" + "-" * 60)
    click.secho(f"  Generating {target_tool} configuration...", bold=True)

    builder = _get_builder(target_tool)
    if builder:
        output_path = Path(".")
        try:
            actions = builder.build(output_path, config=config, dry_run=False)
            for action in actions:
                click.echo(f"    {action}")
        except Exception as e:
            click.secho(f"\n  Error building configuration: {e}", fg="red", err=True)
            click.secho(
                "  Note: Old artifacts may have been removed. Run 'prompticorn init' to restore.",
                fg="yellow",
                err=True,
            )
            raise click.Abort() from e

        # Save tool selection to config
        config["ai_tool"] = target_tool
        ConfigHandler.save_config(config)
    else:
        click.secho(f"  Error: Unknown tool: {target_tool}", fg="red")
        raise click.Abort()

    click.echo("\n" + "=" * 60)
    click.secho(f"  Switched to {target_tool}!", bold=True, fg="green")
    click.echo("=" * 60)


# ══ swap ═════════════════════════════════════════════════════════════════════════


@cli.command("swap")
def swap_command():
    """
    Swap active personas and regenerate configurations.

    Changes which personas (roles) are active, filtering which agents are
    generated. This allows switching between different team configurations
    or filtering agents for different workflows.

    After swapping, all registered configuration files are regenerated with
    only the agents relevant to the selected personas.

    Personas determine which agents are included:
    - software_engineer: code, test, refactor, migration
    - qa_tester: test, review
    - devops_engineer: devops, observability, incident
    - backend_software_engineer, frontend_software_engineer, fullstack_software_engineer
    - And more based on configured personas

    Universal agents (ask, debug, explain, plan, orchestrator) are always
    generated regardless of persona selection.

    Usage:
        prompticorn swap

    Allows selecting multiple personas to combine agent sets.
    """

    from prompticorn.ui._selector import select_option_with_explain
    from prompticorn.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'prompticorn init' first.",
            fg="red",
        )
        raise click.Abort()

    config = ConfigHandler.load_config()

    # Get current tool
    artifact_manager = ToolOutputManager()
    current_tool = artifact_manager.current_tool

    if not current_tool:
        click.secho(
            "Error: No AI tool configured. Run 'prompticorn init' first.",
            fg="red",
        )
        raise click.Abort()

    # Load persona registry
    try:
        persona_registry = PersonaRegistry.from_resolver()
    except Exception as e:
        click.secho(f"Error: Could not load personas ({e})", fg="red")
        raise click.Abort() from e

    # Get current active personas
    current_personas = config.get("active_personas", [])

    # Build options and explanations for persona selection
    persona_ids = persona_registry.list_personas()
    persona_options = [persona_registry.get_display_name(pid) for pid in persona_ids]
    persona_explanations = {
        persona_registry.get_display_name(pid): persona_registry.get_description(pid)
        for pid in persona_ids
    }

    # Map display names to IDs
    display_to_id = {persona_registry.get_display_name(pid): pid for pid in persona_ids}
    id_to_display = {pid: persona_registry.get_display_name(pid) for pid in persona_ids}

    # Calculate default indices (currently selected personas)
    default_indices = []
    for idx, persona_id in enumerate(persona_ids):
        if persona_id in current_personas:
            default_indices.append(idx)

    click.echo("\n" + "=" * 60)
    click.secho("  Swap Personas", bold=True, fg="cyan")
    click.echo("=" * 60)

    if current_personas:
        current_display = [id_to_display[pid] for pid in current_personas]
        click.echo(f"\n  Current personas: {', '.join(current_display)}")
    else:
        click.echo("\n  Current personas: (none selected)")

    # Show interactive persona selection
    try:
        selected_personas_display = select_option_with_explain(
            question="Which personas will be working on this codebase?",
            options=persona_options,
            explanations=persona_explanations,
            question_explanation="Select one or more roles. Only agents/workflows for selected personas will be generated.",
            default_indices=set(default_indices),
            allow_multiple=True,
        )

        # Convert display names back to persona IDs
        if isinstance(selected_personas_display, list):
            selected_persona_ids = [
                display_to_id[display_name] for display_name in selected_personas_display
            ]
        else:
            # Single selection (shouldn't happen with allow_multiple=True, but handle it)
            selected_persona_ids = [display_to_id[selected_personas_display]]

    except UserCancelledError:
        click.echo("\nOperation cancelled.")
        raise click.Abort() from None

    # Check if selection changed
    if set(selected_persona_ids) == set(current_personas):
        click.echo("\n" + "=" * 60)
        click.secho("  No changes made - personas unchanged", bold=True, fg="yellow")
        click.echo("=" * 60)
        return

    # Update config with new personas
    config["active_personas"] = selected_persona_ids

    # Show what's changing
    click.echo("\n" + "-" * 60)
    click.secho("  Persona Changes", bold=True)
    click.echo("-" * 60)

    removed = set(current_personas) - set(selected_persona_ids)
    added = set(selected_persona_ids) - set(current_personas)

    if removed:
        removed_display = [id_to_display.get(pid) or pid for pid in removed]
        click.echo(f"  Removed: {', '.join(removed_display)}")

    if added:
        added_display = [id_to_display.get(pid) or pid for pid in added]
        click.echo(f"  Added: {', '.join(added_display)}")

    # Remove old artifacts and regenerate
    click.echo("\n" + "-" * 60)
    click.secho("  Removing old artifacts...", bold=True)

    # Remove current tool's CREATE artifacts (the .kilo/ directory itself)
    # NOT the artifacts from other tools
    import shutil

    artifacts_to_remove = artifact_manager.outputs_to_create(current_tool)
    removal_actions = []
    for artifact in artifacts_to_remove:
        artifact_path = Path(artifact)
        if artifact_path.exists():
            if artifact_path.is_dir():
                shutil.rmtree(artifact_path)
                removal_actions.append(f"Removed directory: {artifact}")
            else:
                artifact_path.unlink()
                removal_actions.append(f"Removed file: {artifact}")

    for action in removal_actions:
        click.echo(f"    {action}")

    # Build new artifacts with updated persona filtering
    click.echo("\n" + "-" * 60)
    click.secho(f"  Regenerating {current_tool} configuration...", bold=True)

    builder = _get_builder(current_tool)
    if builder:
        output_path = Path(".")
        try:
            actions = builder.build(output_path, config=config, dry_run=False)
            for action in actions:
                click.echo(f"    {action}")
        except Exception as e:
            click.secho(f"\n  Error regenerating configuration: {e}", fg="red", err=True)
            click.secho(
                "  Note: Old artifacts were removed. Run 'prompticorn init' to restore.",
                fg="yellow",
                err=True,
            )
            raise click.Abort() from e

        # Save updated config
        ConfigHandler.save_config(config)
    else:
        click.secho(f"  Error: Unknown tool: {current_tool}", fg="red")
        raise click.Abort()

    click.echo("\n" + "=" * 60)
    click.secho("  Personas swapped successfully!", bold=True, fg="green")
    click.echo("=" * 60)

    # Show summary
    new_display = [id_to_display[pid] for pid in selected_persona_ids]
    click.echo(f"\n  Active personas: {', '.join(new_display)}")
    click.echo()


# ══ update ═══════════════════════════════════════════════════════════════════════


@cli.command("update")
def update_command():
    """
    Update configuration options interactively.

    Allows modifying existing configuration values without re-running the
    full initialization flow. Updates .prompticorn.yaml with new values
    and shows which options have changed.

    You can update:
    - Language
    - Runtime version
    - Package manager
    - Testing framework
    - And other language-specific settings

    Changes are only saved when you explicitly select "Save & Exit".

    Usage:
        prompticorn update

    Interactive menu shows:
    - Current value for each option
    - Options marked as [changed] in green if modified
    - "Save & Exit" option to save and exit
    """

    from prompticorn.ui._selector import select_option_with_explain
    from prompticorn.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'prompticorn init' first.",
            fg="red",
        )
        raise click.Abort()

    config = ConfigHandler.load_config()

    # Load current values
    options = load_current_values(config, CONFIG_OPTIONS.copy())
    changed_keys: set[str] = set()

    while True:
        # Build display options
        display_options = []
        for opt in options:
            is_changed = opt.key in changed_keys
            value_str = str(opt.current_value) if opt.current_value else "[not set]"

            if is_changed:
                display_name = f"{opt.display_name} [{click.style('changed', fg='green')}]"
            else:
                display_name = opt.display_name

            display_options.append((opt.key, value_str, display_name))

        # Show menu
        try:
            selected = select_option_with_explain(
                question="Select an option to modify (or select 'Save & Exit' to save):",
                options=[opt[0] for opt in display_options] + ["Save & Exit"],
                explanations={opt[0]: f"{opt[2]}: {opt[1]}" for opt in display_options},
                question_explanation="Use up/down arrows to navigate, Enter to select.\nCurrent values are shown in blue, changes in green.",
                default_index=len(display_options),  # Default to Save & Exit
                allow_multiple=False,
            )
            assert isinstance(selected, str), "allow_multiple=False should return str"
            selected = selected
        except UserCancelledError:
            click.echo("\nOperation cancelled. No changes saved.")
            raise click.Abort() from None

        if selected == "Save & Exit":
            # Save configuration
            ConfigHandler.save_config(config)
            click.echo("\n" + "=" * 60)
            click.secho("  Configuration saved!", bold=True, fg="green")
            click.echo("=" * 60)
            return

        # Find the selected option
        selected_opt = next((opt for opt in options if opt.key == selected), None)
        if selected_opt is None:
            continue

        # Handle the option based on its type
        if selected_opt.option_type == "single-select" and selected_opt.available_options:
            # Single-select option
            try:
                new_value = select_option_with_explain(
                    question=f"Select {selected_opt.display_name}:",
                    options=selected_opt.available_options,
                    explanations={opt: f"Select {opt}" for opt in selected_opt.available_options},
                    question_explanation=f"Choose a {selected_opt.display_name.lower()} for your project.",
                    default_index=0,
                    allow_multiple=False,
                )
                assert isinstance(new_value, str), "allow_multiple=False should return str"
            except UserCancelledError:
                continue
        elif selected_opt.option_type == "text":
            # Text input
            new_value = click.prompt(
                f"\nEnter {selected_opt.display_name}:",
                default=str(selected_opt.current_value) if selected_opt.current_value else "",
                show_default=True,
            )
        else:
            # Composite or unknown type - skip for now
            click.secho(
                f"  Editing {selected_opt.option_type} options is not yet supported.",
                fg="yellow",
            )
            continue

        # Update the value
        if new_value:
            set_nested_value(config, selected_opt.key, new_value)
            changed_keys.add(selected_opt.key)
            # Update the option's current value
            selected_opt.current_value = new_value


def _get_builder(tool: str):
    """Get the builder adapter for a given tool.

    This function returns a prompt builder instance that maintains compatibility
    with the legacy builder interface while using the new IR-based system internally.

    Args:
        tool: The tool name (e.g., 'kilo-cli', 'kilo-ide', 'cline', 'cursor', 'copilot').

    Returns:
        PromptBuilder instance for the given tool.

    Raises:
        ValueError: If tool is unknown.
    """
    from prompticorn.prompt_builder import get_prompt_builder

    return get_prompt_builder(tool)


# ── lock / build ───────────────────────────────────────────────────────────


def _utc_now() -> str:
    """Current time in the lock's one canonical spelling."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_config():
    """Load the manifest, or abort with the standard message."""
    if not ConfigHandler.config_exists():
        click.secho("Error: No configuration found. Run 'prompticorn init' first.", fg="red")
        raise click.Abort()
    return ConfigHandler.load_config()


def _selected_tool(config: dict) -> str | None:
    """The tool this project builds for, if one has been chosen."""
    tool = config.get("ai_tool")
    return tool if isinstance(tool, str) and tool else None


def _output_paths_for(tool: str) -> tuple[str, ...]:
    """The roots a tool emits, used to digest outputs into the lock."""
    return tuple(sorted(ToolOutputManager().outputs_to_create(tool)))


@cli.command("lock")
def lock_command():
    """
    Resolve the manifest and write .prompticorn/prompticorn.lock.

    Records what this project resolved to — artifact versions and digests, every
    content unit with the layer that supplied it, and the digest of each
    generated file — so a later build can tell whether anything moved.

    Re-running with nothing changed rewrites nothing: the lock is committed, and
    a file that churns on every run is one reviewers stop reading.

    Exit codes:
        0  lock written or already up to date
        3  an existing lock is unusable (corrupt, or from a newer prompticorn)

    Usage:
        prompticorn lock
    """
    from prompticorn.lockfile import ExitCode, LockService

    config = _require_config()
    root = Path(".")
    tool = _selected_tool(config)
    output_paths = _output_paths_for(tool) if tool else ()

    outcome = LockService.inspect(root, config, _utc_now(), output_paths)
    if outcome.is_unusable:
        click.secho(f"\n✗ {outcome.unusable_reason}", fg="red", err=True)
        sys.exit(ExitCode.UNUSABLE_LOCK)

    changed = LockService.write(root, outcome.lock)
    location = LockService.lock_path(root)
    if changed:
        click.secho(f"\n✓ Wrote {location}", fg="green")
    else:
        click.echo(f"\n  {location} is already up to date.")
    sys.exit(ExitCode.CLEAN)


@cli.command("verify")
def verify_command():
    """
    Check that generated output still matches the lock, and nothing extra exists.

    This is the CI gate that makes the source/generated wall real rather than a
    convention people are asked to respect. It answers three questions:

    \b
      1. Does every output the lock names still exist, unmodified?
      2. Is there anything in the generated directories the lock does not know
         about? Without this, a rogue agent added to .claude/agents/ passes
         unnoticed, which defeats the point of checking at all.
      3. Does the lock carry a digest for every unit it references?

    Digests cover the file body with the provenance header stripped, the same
    way .prompticorn/provenance.json digests it, so a version bump that changed
    no content does not read as a modified file.

    Nothing is written. Every finding is reported, not just the first.

    \b
    Exit codes:
        0  clean; outputs match the lock and nothing extra exists
        1  outputs are missing, or files exist that the lock does not know about
        3  the lock is unusable (corrupt, or from a newer prompticorn)
        4  a generated file was modified by hand

    \b
    Usage:
        prompticorn verify
    """
    from prompticorn.lockfile import ExitCode, LockService
    from prompticorn.lockfile.errors import LockError
    from prompticorn.lockfile.lock_reader import LockReader
    from prompticorn.verify import OutputVerifier

    config = _require_config()
    root = Path(".")
    tool = _selected_tool(config)
    if tool is None:
        click.secho("\n✗ No tool is selected; run `prompticorn switch` first.", fg="red", err=True)
        sys.exit(ExitCode.DRIFT)

    location = LockService.lock_path(root)
    if not location.is_file():
        click.secho(f"\n✗ No lock at {location}. Run `prompticorn lock` first.", fg="red", err=True)
        sys.exit(ExitCode.UNUSABLE_LOCK)

    try:
        lock = LockReader.read(location)
    except LockError as error:
        click.secho(f"\n✗ {error}", fg="red", err=True)
        sys.exit(ExitCode.UNUSABLE_LOCK)

    report = OutputVerifier(root=root, tool=tool).verify(lock)
    code = report.exit_code
    if report.is_clean:
        click.secho(f"\n✓ {report.render()}", fg="green")
    else:
        click.secho(f"\n{report.render()}", fg="red" if report.has_tampering else "yellow")
    sys.exit(code)


@cli.command("regenerate")
def regenerate_command():
    """
    Rebuild the generated tree from the lock, discarding whatever is there now.

    This is the answer to a hand-edited generated file: recompile, don't edit.
    Generated directories are disposable — this deletes the ones the selected
    tool owns and rebuilds them, then checks the result against the lock.

    \b
    Unlike `build`, nothing is re-resolved and nothing is written to the lock.
    If the sources no longer match what the lock recorded, the rebuild is
    refused rather than quietly producing a tree the lock does not describe.

    \b
    Exit codes:
        0  the tree was rebuilt and matches the lock
        1  the sources moved, so nothing was regenerated
        3  there is no lock, or it is unusable
        4  the rebuild did not reproduce the lock (a defect; please report it)

    \b
    Usage:
        prompticorn regenerate
    """
    from prompticorn.lockfile import ExitCode, LockService
    from prompticorn.lockfile.errors import LockError
    from prompticorn.lockfile.lock_reader import LockReader
    from prompticorn.regenerate import RegenerationService

    config = _require_config()
    root = Path(".")

    tool = _selected_tool(config)
    if tool is None:
        click.secho("\n✗ No tool is selected; run `prompticorn switch` first.", fg="red", err=True)
        sys.exit(ExitCode.DRIFT)

    builder = _get_builder(tool)
    if builder is None:
        click.secho(f"Error: Unknown tool: {tool}", fg="red")
        raise click.Abort()

    location = LockService.lock_path(root)
    if not location.is_file():
        click.secho(
            f"\n✗ No lock at {location}. Run `prompticorn lock` first — there is "
            "nothing to regenerate from.",
            fg="red",
            err=True,
        )
        sys.exit(ExitCode.UNUSABLE_LOCK)

    try:
        lock = LockReader.read(location)
    except LockError as error:
        click.secho(f"\n✗ {error}", fg="red", err=True)
        sys.exit(ExitCode.UNUSABLE_LOCK)

    click.secho(f"\n  Regenerating {tool} configuration from {location}...", bold=True)
    report = RegenerationService(root=root, tool=tool, config=config).regenerate(
        lock, builder, _utc_now()
    )

    for action in (*report.removed, *report.rebuilt):
        click.echo(f"    {action}")

    if report.is_clean:
        click.secho(f"\n✓ {report.render()}", fg="green")
    else:
        click.secho(f"\n{report.render()}", fg="red" if report.refused else "yellow")
    sys.exit(report.exit_code)


@cli.command("build")
@click.option(
    "--frozen",
    is_flag=True,
    help="Fail instead of re-resolving if the lock and reality diverge.",
)
def build_command(frozen: bool):
    """
    Regenerate configuration for the currently selected tool.

    Unlike `switch`, this does not change which tool is selected and does not
    remove another tool's files — it rebuilds what is already configured.

    With --frozen, nothing is written to the lock and any divergence is an
    error. That is the mode for CI: it answers "would this build differ from
    what was committed?" without quietly making the answer no.

    Exit codes:
        0  clean; outputs match the lock
        1  the lock and reality diverge (--frozen only)
        3  the lock is unusable (corrupt, or from a newer prompticorn)

    Usage:
        prompticorn build
        prompticorn build --frozen
    """
    from prompticorn.lockfile import ExitCode, LockService

    config = _require_config()
    root = Path(".")

    tool = _selected_tool(config)
    if tool is None:
        click.secho(
            "Error: No tool selected. Run 'prompticorn switch <tool>' first.",
            fg="red",
        )
        raise click.Abort()

    builder = _get_builder(tool)
    if builder is None:
        click.secho(f"Error: Unknown tool: {tool}", fg="red")
        raise click.Abort()

    click.secho(f"\n  Generating {tool} configuration...", bold=True)
    try:
        for action in builder.build(root, config=config, dry_run=False):
            click.echo(f"    {action}")
    except Exception as exc:
        click.secho(f"\n  Error building configuration: {exc}", fg="red", err=True)
        raise click.Abort() from exc

    outcome = LockService.inspect(root, config, _utc_now(), _output_paths_for(tool))

    if outcome.is_unusable:
        click.secho(f"\n✗ {outcome.unusable_reason}", fg="red", err=True)
        sys.exit(ExitCode.UNUSABLE_LOCK)

    if not outcome.had_existing_lock:
        # Not an error: a project without a lock is simply one that has not
        # opted in yet, and refusing to build would make the feature a tax.
        from prompticorn.lockfile import NO_LOCK_HINT

        click.echo(f"\n  {NO_LOCK_HINT}")
        sys.exit(ExitCode.CLEAN)

    if outcome.report.is_clean:
        click.secho("\n✓ No drift: outputs match the lock.", fg="green")
        sys.exit(ExitCode.CLEAN)

    click.echo("\n" + outcome.report.render())

    if frozen:
        # Deliberately no write. A frozen build that re-locked would report drift
        # once and never again, which defeats the entire point of the flag.
        click.secho("\n✗ Frozen build: refusing to re-resolve.", fg="red", err=True)
        sys.exit(ExitCode.DRIFT)

    LockService.write(root, outcome.lock)
    click.secho(f"\n✓ Updated {LockService.lock_path(root)}", fg="yellow")
    sys.exit(ExitCode.CLEAN)


# ── validate ───────────────────────────────────────────────────────────────


@cli.command("status")
def status_command():
    """
    Show what this repository has installed, and where it sits in the store.

    Reads the machine-local index under `~/.prompticorn`, which records what
    every repository on this machine resolved to. The index is a convenience,
    never an authority: this project's lock is the truth about this project, and
    the index is refreshed from it on every run.

    \b
    Usage:
        prompticorn status
    """
    from prompticorn.store import InstallIndex, InstallRecorder, home

    root = Path(".")
    click.echo(f"\n  Store:   {home()}")
    click.echo(f"  Project: {root.resolve()}")

    with InstallIndex() as index:
        identity = InstallRecorder(index=index).record(root, _utc_now())
        if identity is None:
            click.echo("\n  No usable lock here — run `prompticorn lock` first.")
            return

        click.echo(f"  Repo id: {identity}")
        installs = index.installs_for(identity)
        if not installs:
            click.echo("\n  The lock records no artifacts.")
            return

        click.echo(f"\n  {len(installs)} artifact(s):")
        for record in installs:
            origin = record.source or "bundled"
            click.echo(f"    {record.artifact_id}  ({origin})")

        elsewhere = {
            other
            for record in installs
            for other in index.repos_with(record.artifact_id)
            if other != identity
        }
        if elsewhere:
            click.echo(
                f"\n  {len(elsewhere)} other repo(s) on this machine share artifacts with it."
            )


@cli.group("cache")
def cache_group():
    """
    Inspect and purge the machine-local blob cache.

    Artifacts fetched from a source are cached under `~/.prompticorn/cas`,
    addressed by the digest of their own content. The cache is shared by every
    repository on this machine and holds nothing that cannot be fetched again,
    so clearing it costs a refetch and nothing else.

    \b
    Usage:
        prompticorn cache status
        prompticorn cache clear
    """


@cache_group.command("status")
def cache_status():
    """
    Report where the cache is and how much it holds.
    """
    from prompticorn.store import BlobStore, home

    store = BlobStore()
    digests = list(store.blobs())
    total = sum(store.path_for(digest).stat().st_size for digest in digests)

    click.echo(f"\n  Store:  {home()}")
    click.echo(f"  Cache:  {store.directory}")
    if not digests:
        click.echo("\n  The cache is empty.")
        return
    click.echo(f"\n  {len(digests)} blob(s), {total / 1024:.1f} KiB")


@cache_group.command("clear")
@click.option("--yes", is_flag=True, help="Do not ask for confirmation.")
def cache_clear(yes: bool):
    """
    Delete every cached blob.

    Safe by construction: the cache is a cache. Anything removed is fetched
    again the next time it is needed.
    """
    from prompticorn.store import BlobStore

    store = BlobStore()
    digests = list(store.blobs())
    if not digests:
        click.echo(f"\n  {store.directory} is already empty.")
        return

    if not yes:
        click.confirm(
            f"\n  Delete {len(digests)} cached blob(s) from {store.directory}?", abort=True
        )

    removed = store.clear()
    click.secho(f"\n\u2713 Cleared {removed} file(s) from {store.directory}", fg="green")


@cli.command("validate")
def validate_prompts():
    """
    Validate agent registry structure and that all agents load cleanly.

    Checks that:
    1. Each agent has a base prompt.md (or minimal/verbose variants)
    2. Each subagent has minimal/verbose variant directories with prompt.md
    3. All discovered agents parse without load errors

    Usage:
        prompticorn validate

    Output:
        ✓ Registry valid: N agents, M subagents.
        or
        ✗ <structural issue>
    """
    from prompticorn.agent_registry import RegistryDiscovery, RegistryLoadError

    click.echo("\n▶ Validating agent registry...\n")
    discovery = RegistryDiscovery(_AGENTS_DIR)
    issues = discovery.validate_structure()

    try:
        agents = discovery.discover()
    except RegistryLoadError as exc:
        issues.append(f"load error: {exc}")
        agents = {}

    if issues:
        for issue in issues:
            click.secho(f"  ✗ {issue}", fg="red")
        click.echo()
        click.secho(f"  {len(issues)} issue(s) found.", fg="red")
        sys.exit(1)

    top_level = [name for name in agents if "/" not in name]
    subagents = [name for name in agents if "/" in name]
    click.secho(
        f"  ✓ Registry valid: {len(top_level)} agents, {len(subagents)} subagents.",
        fg="green",
    )
    click.echo()


@cli.command("package-skills")
@click.option(
    "--source",
    "source",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory of emitted skills (each <name>/SKILL.md). "
    "Defaults to the first of .claude/skills, .agents/skills, .github/skills.",
)
@click.option(
    "--output",
    "output",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("dist/claude-desktop-skills"),
    show_default=True,
    help="Directory to write the per-skill .zip files into.",
)
def package_skills_cmd(source: Path | None, output: Path):
    """
    Package emitted Agent Skills into claude.ai / Claude Desktop upload zips.

    Claude Desktop has no on-disk skill path, so its custom skills are uploaded
    by hand (Settings > Features) as one zip per skill. This bundles each emitted
    ``<name>/SKILL.md`` folder into ``<name>.zip`` in the structure claude.ai
    accepts. Run a build first (e.g. ``prompticorn switch claude``) so a skills
    directory exists.

    Usage:
        prompticorn package-skills
        prompticorn package-skills --source .claude/skills --output dist/skills
    """
    from prompticorn.skills_packager import package_skills

    if source is None:
        candidates = [Path(".claude/skills"), Path(".agents/skills"), Path(".github/skills")]
        source = next((c for c in candidates if c.is_dir()), None)
        if source is None:
            click.secho(
                "  ✗ No emitted skills directory found. Run a build first "
                "(e.g. `prompticorn switch claude`), or pass --source.",
                fg="red",
            )
            sys.exit(1)

    click.echo(f"\n▶ Packaging skills from {source} ...\n")
    try:
        results = package_skills(source, output)
    except FileNotFoundError as exc:
        click.secho(f"  ✗ {exc}", fg="red")
        sys.exit(1)

    packaged = [r for r in results if r.ok]
    skipped = [r for r in results if not r.ok]
    for result in skipped:
        click.secho(f"  ⚠ skipped {result.name}: {result.skipped_reason}", fg="yellow")
    click.secho(f"  ✓ Packaged {len(packaged)} skill(s) into {output}/", fg="green")
    if skipped:
        click.secho(f"  ⚠ {len(skipped)} skipped (see above).", fg="yellow")
    click.echo("\n  Upload each .zip via claude.ai Settings > Features.\n")
