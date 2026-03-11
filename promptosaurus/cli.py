"""CLI module for prompt library management.

This module provides the command-line interface for managing AI assistant
configurations. It uses Click to define the CLI commands and orchestrates
the configuration, question handling, and output generation.

Commands:
    prompt init      - Interactive setup for AI assistant configurations
    prompt list      - Show all registered modes and their prompt files
    prompt validate  - Check for missing files and unregistered orphans

Example:
    >>> from promptosaurus.cli import cli
    >>> # CLI is invoked via: prompt init

Key Functions:
    - cli: Main Click group for the prompt command
    - list_prompts: Display all registered modes and their files
    - init_prompts: Interactive initialization workflow
    - update_config: Update configuration options
    - switch_tool: Switch between AI tools
    - validate_prompts: Validate configuration integrity
"""

import sys
from pathlib import Path
from typing import Any, cast

import click

from promptosaurus.artifacts import ArtifactManager
from promptosaurus.cli_utils import (
    get_supported_tools_display,
    normalize_tool_name,
    validate_tool_name,
)
from promptosaurus.config_handler import (
    DEFAULT_CONFIG_TEMPLATE,
    DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE,
    ConfigHandler,
)
from promptosaurus.config_options import (
    CONFIG_OPTIONS,
    load_current_values,
    set_nested_value,
)
from promptosaurus.questions.base.constants import (
    REPO_TYPE_MULTI_MONOREPO,
    REPO_TYPE_SINGLE,
)
from promptosaurus.questions.base.folder_spec import (
    FOLDER_TYPE_PRESETS,
    FolderSpec,
)
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion
from promptosaurus.questions.language import LANGUAGE_KEYS
from promptosaurus.registry import registry

# Valid languages for each preset type/subtype
PRESET_VALID_LANGUAGES: dict[str, dict[str, list[str]]] = {
    "backend": {
        "api": [
            "python",
            "typescript",
            "javascript",
            "go",
            "java",
            "rust",
            "csharp",
            "ruby",
            "php",
        ],
        "library": [
            "python",
            "typescript",
            "javascript",
            "go",
            "java",
            "rust",
            "csharp",
            "ruby",
            "php",
        ],
        "worker": ["python", "go", "rust", "java"],
        "cli": ["python", "go", "rust", "csharp", "ruby", "php"],
    },
    "frontend": {
        "ui": ["typescript", "javascript"],
        "library": ["typescript", "javascript"],
        "e2e": ["typescript", "javascript", "python"],
    },
}


def _get_valid_languages(preset_type: str, subtype: str) -> list[str]:
    """Get valid languages for a preset type/subtype.

    Args:
        preset_type: The folder type (backend or frontend)
        subtype: The folder subtype

    Returns:
        List of valid language keys
    """
    if preset_type in PRESET_VALID_LANGUAGES:
        if subtype in PRESET_VALID_LANGUAGES[preset_type]:
            return PRESET_VALID_LANGUAGES[preset_type][subtype]
    # Fallback to common languages if not found
    return ["python", "typescript", "javascript", "go", "java", "rust"]


def _setup_monorepo_folders() -> list[dict[str, Any]]:
    """Interactive setup for monorepo folder configuration.

    This function prompts the user to add folders to their monorepo,
    either through standard presets (frontend/backend) or custom paths.

    Returns:
        List of folder specifications.
    """
    from promptosaurus.ui._selector import select_option_with_explain

    folder_specs: list[dict[str, Any]] = []
    add_more = True

    while add_more:
        click.echo("\n" + "-" * 60)
        click.secho("  Add Folder", bold=True)
        click.echo("-" * 60)

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

        # folder_type is str when allow_multiple=False
        if not isinstance(folder_type, str):
            click.secho("  Error: Expected single selection. Try again.", fg="red")
            continue

        if folder_type == "custom":
            # Custom folder: prompt for folder path
            folder_path = click.prompt(
                "\nFolder path (e.g., services/auth/api)",
                default="",
            ).strip()

            if not folder_path:
                click.secho("  Folder path cannot be empty. Skipping.", fg="yellow")
                continue

            # Prompt for language
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
            subtypes = list(FOLDER_TYPE_PRESETS[preset_type].keys())
            subtype_options = [
                f"{s} ({FOLDER_TYPE_PRESETS[preset_type][s]['language']})" for s in subtypes
            ]

            # Step 2: Ask for subtype
            subtype_choice = cast(
                str,
                select_option_with_explain(
                    question=f"What {preset_type} subtype?",
                    options=subtype_options,
                    explanations={
                        f"{s} ({FOLDER_TYPE_PRESETS[preset_type][s]['language']})": f"{preset_type.capitalize()} {s} - uses {FOLDER_TYPE_PRESETS[preset_type][s]['language']}"
                        for s in subtypes
                    },
                    question_explanation=f"Select the {preset_type} subtype to create",
                    default_index=0,
                    allow_multiple=False,
                ),
            )
            # subtype_choice is str when allow_multiple=False
            subtype = subtype_choice.split(" (")[0]  # Extract subtype name

            # Step 3: Ask for folder path
            folder_path = click.prompt(
                f"\nFolder path (e.g., {preset_type}/{subtype})",
                default=f"{preset_type}/{subtype}",
            ).strip()

            if not folder_path:
                folder_path = f"{preset_type}/{subtype}"

            # Get preset defaults
            preset_defaults = FOLDER_TYPE_PRESETS[preset_type][subtype]
            default_language = preset_defaults["language"]

            # Step 4: Ask for language - filter to valid languages for this preset
            valid_languages = _get_valid_languages(preset_type, subtype)

            # Ensure default is in the list and at the front
            if default_language not in valid_languages:
                valid_languages.insert(0, default_language)

            language_choice = cast(
                str,
                select_option_with_explain(
                    question="Programming language?",
                    options=valid_languages,
                    explanations={
                        lang: f"Use {lang} for this {preset_type}/{subtype} folder"
                        for lang in valid_languages
                    },
                    question_explanation=f"Select language for {folder_path}. Default is {default_language} based on preset.",
                    default_index=0,
                    allow_multiple=False,
                ),
            )
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

    click.echo("\n" + "-" * 60)
    click.secho(f"  Configuring: {folder_path} ({language})", bold=True)
    click.echo("-" * 60)

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
    pipeline for each folder's language.

    Note: This is a batch operation that runs AFTER all folders are added.
    For inline language questions during folder creation, use _ask_language_questions_for_folder.

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

    updated_specs: list[dict[str, Any]] = []

    for spec in folder_specs:
        folder_path = spec.get("folder", "")
        language = spec.get("language", "")

        if not language:
            updated_specs.append(spec)
            continue

        click.echo("\n" + "-" * 60)
        click.secho(f"  Configuring: {folder_path} ({language})", bold=True)
        click.echo("-" * 60)

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
    """Prompt library CLI — manage and validate your prompt configurations.

    Edit files in prompts/, then use `prompt list` to see available modes and
    `prompt validate` to check configuration integrity.
    """


# ── list ───────────────────────────────────────────────────────────────────────


@cli.command("list")
def list_prompts():
    """List all registered modes and their prompt files."""
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

    Walks through questions to set up .promptosaurus/.promptosaurus.yaml with
    your language, runtime, package manager, testing framework, and more.
    Then generates AI assistant configurations for selected tools.
    """

    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    click.echo("\n" + "=" * 60)
    click.secho("  Prompt CLI Initialization", bold=True, fg="cyan")
    click.echo("=" * 60)
    click.echo("\nUse ↑/↓ arrows, numbers, or Enter for defaults.")

    try:
        # Step 1: Select which AI assistant to configure
        ai_tool = select_option_with_explain(
            question="Which AI assistant would you like to configure?",
            options=["kilo-cli", "kilo-ide", "cline", "cursor", "copilot"],
            explanations={
                "kilo-cli": "Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
                "kilo-ide": "Kilo Code (IDE) - .kilocode/rules-{mode}/ directory structure",
                "cline": "Cline - .clinerules file (concatenated rules)",
                "cursor": "Cursor - .cursor/rules/ directory + .cursorrules",
                "copilot": "GitHub Copilot - .github/copilot-instructions.md",
            },
            question_explanation="Select one AI assistant to configure.",
            default_index=1,
            allow_multiple=False,
        )
        # Wrap single selection in list for consistent handling
        ai_tools: list[str] = [cast(str, ai_tool)]

        # Step 2: Repository type
        click.echo("\n" + "-" * 60)
        repo_question = RepositoryTypeQuestion()
        default_idx = repo_question.options.index(repo_question.default)

        repo_type = select_option_with_explain(
            question=repo_question.question_text,
            options=repo_question.options,
            explanations=repo_question.option_explanations,
            question_explanation=repo_question.explanation,
            default_index=default_idx,
        )

        # Step 3 & 4: Handle language questions based on repo type
        # Use isinstance() for proper type narrowing from str | list[str] to str
        if isinstance(repo_type, str) and repo_type == REPO_TYPE_SINGLE:
            from promptosaurus.questions.handlers.handle_single_language_questions import (
                HandleSingleLanguageQuestions,
            )

            handler = HandleSingleLanguageQuestions(select_option_with_explain)
            config: dict[str, Any] = handler.handle(repo_type)
        else:
            # Multi-folder or mixed - just save repo type for now
            if repo_type == REPO_TYPE_MULTI_MONOREPO:
                # Interactive folder setup for multi-language monorepo
                config = DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE.copy()
                config["repository"]["type"] = repo_type

                # Run interactive folder setup
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
                config = DEFAULT_CONFIG_TEMPLATE.copy()
                config["repository"]["type"] = repo_type

        # Save configuration
        ConfigHandler.save_config(config)

        click.echo("\n\n" + "=" * 60)
        click.secho("  Configuration saved!", bold=True, fg="green")
        click.echo("=" * 60)
        click.echo(f"\n  Config file: {ConfigHandler.get_config_path()}")

        # Step 5: Generate selected AI assistant configurations
        if ai_tools:
            click.echo("\n" + "-" * 60)
            click.secho("  Generating AI assistant configurations...", bold=True)
            click.echo("-" * 60)

            output_path = Path(".")
            for tool in ai_tools:
                builder_class = _get_builder(tool)  # type: ignore[arg-type]
                if builder_class:
                    builder = builder_class()
                    actions = builder.build(output_path, config=config, dry_run=False)
                    for action in actions:
                        click.echo(f"  {action}")
                else:
                    click.secho(f"  ✗ Unknown tool: {tool}", fg="yellow")

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
    """Switch to a different AI assistant tool.

    Usage:
        prompt switch kilo-ide    # Switch directly
        prompt switch             # Interactive menu
    """
    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'prompt init' first.",
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
            tool_options = ["kilo-cli", "kilo-ide", "cline", "cursor", "copilot"]
            target_tool = cast(
                str,
                select_option_with_explain(
                    question="Which AI assistant would you like to switch to?",
                    options=tool_options,
                    explanations={
                        "kilo-cli": "Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
                        "kilo-ide": "Kilo Code (IDE) - .kilocode/rules-{mode}/ directory structure",
                        "cline": "Cline - .clinerules file (concatenated rules)",
                        "cursor": "Cursor - .cursor/rules/ directory + .cursorrules",
                        "copilot": "GitHub Copilot - .github/copilot-instructions.md",
                    },
                    question_explanation="Select an AI assistant to switch to.",
                    default_index=1,
                    allow_multiple=False,
                ),
            )
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

    builder_class = _get_builder(target_tool)
    if builder_class:
        builder = builder_class()
        output_path = Path(".")
        try:
            actions = builder.build(output_path, config=config, dry_run=False)
            for action in actions:
                click.echo(f"    {action}")
        except Exception as e:
            click.secho(f"\n  Error building configuration: {e}", fg="red", err=True)
            click.secho(
                "  Note: Old artifacts may have been removed. Run 'prompt init' to restore.",
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


# ══ update ═══════════════════════════════════════════════════════════════════════


@cli.command("update")
def update_command():
    """Update configuration options interactively.

    Usage:
        prompt update
    """
    from promptosaurus.ui._selector import select_option_with_explain
    from promptosaurus.ui.exceptions import UserCancelledError

    # Check if config exists
    if not ConfigHandler.config_exists():
        click.secho(
            "Error: No configuration found. Run 'prompt init' first.",
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
                question_explanation="Use ↑/↓ arrows to navigate, Enter to select.\nCurrent values are shown in blue, changes in green.",
                default_index=len(display_options),  # Default to Save & Exit
                allow_multiple=False,
            )
            selected = cast(str, selected)
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
                new_value = cast(
                    str,
                    select_option_with_explain(
                        question=f"Select {selected_opt.display_name}:",
                        options=selected_opt.available_options,
                        explanations={
                            opt: f"Select {opt}" for opt in selected_opt.available_options
                        },
                        question_explanation=f"Choose a {selected_opt.display_name.lower()} for your project.",
                        default_index=0,
                        allow_multiple=False,
                    ),
                )
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
    """Get the builder class for a given tool.

    This function maps a tool name to its corresponding builder class.
    It imports the builder classes lazily to avoid circular imports.

    Args:
        tool: The tool name (e.g., 'kilo-cli', 'kilo-ide', 'cline', 'cursor', 'copilot').

    Returns:
        The builder class for the given tool, or None if tool is not recognized.

    Example:
        >>> builder_class = _get_builder('kilo-cli')
        >>> builder_class is not None
        True
    """
    from promptosaurus.builders.cline import ClineBuilder
    from promptosaurus.builders.copilot import CopilotBuilder
    from promptosaurus.builders.cursor import CursorBuilder
    from promptosaurus.builders.kilo.kilo_cli import KiloCLIBuilder
    from promptosaurus.builders.kilo.kilo_ide import KiloIDEBuilder

    builders = {
        "kilo-cli": KiloCLIBuilder,
        "kilo-ide": KiloIDEBuilder,
        "cline": ClineBuilder,
        "cursor": CursorBuilder,
        "copilot": CopilotBuilder,
    }
    return builders.get(tool)


# ── validate ───────────────────────────────────────────────────────────────────


@cli.command("validate")
def validate_prompts():
    """
    Check that all registered prompt files exist and no files in prompts/
    are unregistered (orphans).
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
