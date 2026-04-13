"""CLI module for prompt library management.

This module provides the command-line interface for managing AI assistant
configurations. It uses Click to define the CLI commands and orchestrates
the configuration, question handling, and output generation.

Commands:
    promptosaurus init      - Interactive setup for AI assistant configurations
    promptosaurus list      - Show all registered modes and their prompt files
    promptosaurus validate  - Check for missing files and unregistered orphans
    promptosaurus switch    - Switch between AI assistant tools
    promptosaurus swap      - Swap active personas and regenerate configurations
    promptosaurus update    - Update configuration options

Key Functions:
    - cli: Main Click group for the promptosaurus CLI
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

from promptosaurus.artifacts import ArtifactManager
from promptosaurus.cli_utils import (
    get_supported_tools_display,
    normalize_tool_name,
    validate_tool_name,
)
from promptosaurus.config_handler import (
    ConfigHandler,
)
from promptosaurus.config_options import (
    CONFIG_OPTIONS,
    load_current_values,
    set_nested_value,
)
from promptosaurus.questions.base.constants import RepositoryTypes
from promptosaurus.questions.base.folder_spec import (
    FolderSpec,
    FolderSpecRegistry,
)
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion
from promptosaurus.questions.language import LANGUAGE_KEYS
from promptosaurus.registry import registry
from promptosaurus.personas import PersonaRegistry

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
    from pathlib import Path
    import yaml
    
    config_file = Path(__file__).parent / "configurations" / "preset_languages.yaml"
    with open(config_file, encoding="utf-8") as f:
        preset_languages = yaml.safe_load(f)
    
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
    from promptosaurus.ui._selector import select_option_with_explain

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
                "backend (preset)": "Backend folder types: api, library, worker, cli",
                "frontend (preset)": "Frontend folder types: ui, library, e2e",
                "custom": "Define your own folder type and configuration",
            },
            question_explanation="Select a folder type: backend (api, library, worker, cli), frontend (ui, library, e2e), or custom",
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
            os.system('clear' if os.name != 'nt' else 'cls')  # Clear screen after curses
            folder_path = click.prompt(
                "\nFolder path (e.g., services/auth/api)",
                default="",
            ).strip()

            if not folder_path:
                click.secho("  Folder path cannot be empty. Skipping.", fg="yellow")
                continue

            # Prompt for language
            os.system('clear' if os.name != 'nt' else 'cls')  # Clear screen
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
                f"{s} ({FolderSpecRegistry.get_folder_type_presets()[preset_type][s]['language']})" for s in subtypes
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
            os.system('clear' if os.name != 'nt' else 'cls')  # Clear screen after curses
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
    from promptosaurus.questions.language import QuestionPipelineError, get_language_questions
    from promptosaurus.ui._selector import select_option_with_explain

    folder_path = spec.get("folder", "")
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

        # Store the answer in the spec
        spec[question.key] = answer

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
    from promptosaurus.questions.language import get_language_questions
    from promptosaurus.ui._selector import select_option_with_explain

    updated_specs: list[dict[str, Any]] = []

    for spec in folder_specs:
        folder_path = spec.get("folder", "")
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

            # Store the answer in the spec
            spec[question.key] = answer

        updated_specs.append(spec)

    return updated_specs


# # ── Initialize registry ───────────────────────────────────────────────────────
# fill_registry()


# ── Root group ─────────────────────────────────────────────────────────────────


@click.group()
def cli():
    """promptosaurus CLI — manage and validate your prompt configurations.

    Edit files in prompts/, then use `promptosaurus list` to see available modes and
    `promptosaurus validate` to check configuration integrity.
    """


# ── list ───────────────────────────────────────────────────────────────────────


@cli.command("list")
def list_prompts():
    """
    List all registered modes and their prompt files.

    Displays a formatted list of all registered prompt files, organized by mode.
    Files marked with ✓ exist on disk, files marked with ✗ MISSING are registered
    but not found.

    Always-on files are displayed first (files included in all modes), followed
    by mode-specific files grouped by mode name.

    Usage:
        promptosaurus list
    """
    always_header = click.style("ALWAYS ON (all modes)", bold=True)
    click.echo(f"\n{always_header}")
    for fname in registry.always_on:
        exists = (
            "✓" if (registry.prompts_dir / fname).exists() else click.style("✗ MISSING", fg="red")
        )
        click.echo(f"  {exists}  {fname}")

    for mode_key, label in registry.modes.items():
        header = click.style(f"\n{label.upper()} MODE  [{mode_key}]", bold=True)
        click.echo(header)
        files = registry.mode_files.get(mode_key, [])
        if not files:
            click.secho("  (no files registered)", fg="yellow")
            continue
        for fname in files:
            exists = (
                "✓"
                if (registry.prompts_dir / fname).exists()
                else click.style("✗ MISSING", fg="red")
            )
            click.echo(f"  {exists}  {fname}")

    click.echo()


# ── init ───────────────────────────────────────────────────────────────────────


@cli.command("init")
def init_prompts():
    """
    Interactively initialize prompt configuration for your project.

    This is the main setup command that walks users through configuration:
    1. Select which AI assistant to configure (Kilo, Cline, Cursor, Copilot)
    2. Choose repository type (single-language or multi-language-monorepo)
    3. Select prompt variant (minimal for efficiency, verbose for detail)
    4. Choose active personas/roles (filters which agents are generated)
    5. Answer language-specific questions
    6. Generate configuration files for the selected AI tool

    Creates or updates .promptosaurus.yaml with the configuration and
    generates tool-specific configuration files in appropriate directories.

    Usage:
        promptosaurus init

    Interactive flow:
        ✓ Select AI tool
        ✓ Choose repository type
        ✓ Select prompt variant
        ✓ Select personas
        ✓ Answer language questions
        ✓ Configuration saved
        ✓ Tool configs generated
    """


    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    # Removed: header stays in buffer when curses exits
    # click.echo("\n" + "=" * 60)
    # Removed: header stays in main buffer after curses exits, causes confusion
    # click.secho("  promptosaurus Initialization", bold=True, fg="cyan")
    # Removed: header stays in buffer when curses exits
    # click.echo("=" * 60)
    # Removed: message stays in main buffer after curses exits
    # click.echo("\nUse up/down arrows, numbers, or Enter for defaults.")

    try:
        # Step 1: Select which AI assistant to configure
        ai_tool = select_option_with_explain(
            question="Which AI assistant would you like to configure?",
            options=["Kilo CLI", "Kilo IDE", "Cline", "Cursor", "Copilot"],
            explanations={
                "Kilo CLI": "Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
                "Kilo IDE": "Kilo Code (IDE) - .kilo/agents/ individual agent files",
                "Cline": "Cline - .clinerules file (concatenated rules)",
                "Cursor": "Cursor - .cursor/rules/ directory + .cursorrules",
                "Copilot": "GitHub Copilot - .github/copilot-instructions.md",
            },
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
            from promptosaurus.personas import PersonaRegistry
            from pathlib import Path
            
            # Load persona registry
            personas_yaml_path = Path(__file__).parent / "personas" / "personas.yaml"
            persona_registry = PersonaRegistry.from_yaml(personas_yaml_path)
            
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
                selected_persona_ids = [display_to_id[display_name] for display_name in selected_personas_display]
            else:
                # Single selection (shouldn't happen with allow_multiple=True, but handle it)
                display_to_id = {persona_registry.get_display_name(pid): pid for pid in persona_ids}
                selected_persona_ids = [display_to_id[selected_personas_display]]
            
            # Store selected personas for later use
            active_personas = selected_persona_ids
            
        except Exception as e:
            # Fallback if persona loading fails - log warning and continue
            click.secho(f"  Warning: Could not load personas ({e}). Skipping persona selection.", fg="yellow")
            active_personas = []  # Empty list = no filtering

        # Step 4: Handle language questions based on repo type
        # Use isinstance() for proper type narrowing from str | list[str] to str
        if isinstance(repo_type, str) and repo_type == RepositoryTypes.SINGLE:
            from promptosaurus.questions.handlers.handle_single_language_questions import (
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
                        folder_path = Path(spec["folder"])
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

        # Save configuration (now includes variant from Step 3)
        ConfigHandler.save_config(config)

        click.echo("\n\n" + "=" * 60)
        click.secho("  Configuration saved!", bold=True, fg="green")
        click.echo("=" * 60)
        click.echo(f"\n  Config file: {ConfigHandler.get_config_path()}")

        # Step 5: Generate selected AI assistant configurations
        if selected_tool:
            click.echo("\n" + "-" * 60)
            click.secho(f"  Generating AI assistant configurations ({variant})...", bold=True)
            click.echo("-" * 60)

            output_path = Path(".")
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
    configurations for the selected tool using the existing .promptosaurus.yaml
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
        promptosaurus switch                  # Interactive menu
        promptosaurus switch kilo-ide        # Switch directly to Kilo IDE
        promptosaurus switch cline           # Switch directly to Cline
    """

    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'promptosaurus init' first.",
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
            tool_options = ["Kilo CLI", "Kilo IDE", "Cline", "Cursor", "Copilot"]
            target_tool_result = select_option_with_explain(
                question="Which AI assistant would you like to switch to?",
                options=tool_options,
                explanations={
                    "Kilo CLI": "Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
                    "Kilo IDE": "Kilo Code (IDE) - .kilo/agents/ individual agent files",
                    "Cline": "Cline - .clinerules file (concatenated rules)",
                    "Cursor": "Cursor - .cursor/rules/ directory + .cursorrules",
                    "Copilot": "GitHub Copilot - .github/copilot-instructions.md",
                },
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
    artifact_manager = ArtifactManager()
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
        removal_actions = artifact_manager.remove_artifacts(current_tool)
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
                "  Note: Old artifacts may have been removed. Run 'promptosaurus init' to restore.",
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
    - software_engineer: code, test, refactor, review, document
    - qa_tester: test, review
    - devops_engineer: deployment, ci-cd, monitoring
    - And more based on configured personas

    Universal agents (ask, debug, explain, plan, orchestrator) are always
    generated regardless of persona selection.

    Usage:
        promptosaurus swap

    Allows selecting multiple personas to combine agent sets.
    """

    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError
    
    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'promptosaurus init' first.",
            fg="red",
        )
        raise click.Abort()
    
    config = ConfigHandler.load_config()
    
    # Get current tool
    artifact_manager = ArtifactManager()
    current_tool = artifact_manager.current_tool
    
    if not current_tool:
        click.secho(
            "Error: No AI tool configured. Run 'promptosaurus init' first.",
            fg="red",
        )
        raise click.Abort()
    
    # Load persona registry
    try:
        personas_yaml_path = Path(__file__).parent / "personas" / "personas.yaml"
        persona_registry = PersonaRegistry.from_yaml(personas_yaml_path)
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
            selected_persona_ids = [display_to_id[display_name] for display_name in selected_personas_display]
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
        removed_display = [id_to_display.get(pid, pid) for pid in removed]
        click.echo(f"  Removed: {', '.join(removed_display)}")
    
    if added:
        added_display = [id_to_display.get(pid, pid) for pid in added]
        click.echo(f"  Added: {', '.join(added_display)}")
    
    # Remove old artifacts and regenerate
    click.echo("\n" + "-" * 60)
    click.secho("  Removing old artifacts...", bold=True)
    
    # Remove current tool's CREATE artifacts (the .kilo/ directory itself)
    # NOT the artifacts from other tools
    import shutil
    artifacts_to_remove = artifact_manager.get_artifacts_to_create(current_tool)
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
                "  Note: Old artifacts were removed. Run 'promptosaurus init' to restore.",
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
    full initialization flow. Updates .promptosaurus.yaml with new values
    and shows which options have changed.

    You can update:
    - Language
    - Runtime version
    - Package manager
    - Testing framework
    - And other language-specific settings

    Changes are only saved when you explicitly select "Save & Exit".

    Usage:
        promptosaurus update

    Interactive menu shows:
    - Current value for each option
    - Options marked as [changed] in green if modified
    - "Save & Exit" option to save and exit
    """

    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'promptosaurus init' first.",
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
    from promptosaurus.prompt_builder import get_prompt_builder

    return get_prompt_builder(tool)


# ── validate ───────────────────────────────────────────────────────────────


@cli.command("validate")
def validate_prompts():
    """
    Validate configuration integrity.

    Checks that:
    1. All registered prompt files exist on disk
    2. No unregistered prompt files (orphans) exist in the prompts/ directory
    3. Configuration format is valid

    Reports missing files (registered but not found) and orphans
    (files that exist but aren't registered).

    Usage:
        promptosaurus validate

    Output:
        ✓ All good — no missing or orphaned files.
        or
        ✗ MISSING: path/to/file.md
        ✗ ORPHAN: path/to/unregistered/file.md
    """
    click.echo("\n▶ Validating prompt registry...\n")
    errors = registry.validate_files()
    if not errors:
        click.secho("  ✓ All good — no missing or orphaned files.", fg="green")
    else:
        for err in errors:
            color = "red" if "MISSING" in err else "yellow"
            click.secho(f"  ✗ {err}", fg=color)
        click.echo()
        click.secho(f"  {len(errors)} issue(s) found.", fg="red")
        sys.exit(1)
    click.echo()
