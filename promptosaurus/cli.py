"""
cli.py
Click-based CLI for the prompt library.

Commands:
  prompt init      - Interactive setup for AI assistant configurations
  prompt list      - Show all registered modes and their prompt files
  prompt validate  - Check for missing files and unregistered orphans
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
from promptosaurus.config_handler import DEFAULT_CONFIG_TEMPLATE, ConfigHandler
from promptosaurus.config_options import (
    CONFIG_OPTIONS,
    load_current_values,
    set_nested_value,
)
from promptosaurus.questions.base.constants import (
    REPO_TYPE_MULTI_FOLDER,
    REPO_TYPE_SINGLE,
)
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion
from promptosaurus.questions.language import LANGUAGE_KEYS
from promptosaurus.registry import registry

# # ── Initialize registry ───────────────────────────────────────────────────────
# fill_registry()


# ── Root group ─────────────────────────────────────────────────────────────────


@click.group()
def cli():
    """
    Prompt library CLI — manage and validate your prompt configurations.

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
            config = DEFAULT_CONFIG_TEMPLATE.copy()
            config["repository"]["type"] = repo_type  # type: ignore[index]
            if repo_type == REPO_TYPE_MULTI_FOLDER:
                click.echo("\n\nFolder mappings will be configured in a future step.")
                click.echo("For now, set up your primary language:")
                language = click.prompt(
                    "\nPrimary language",
                    type=click.Choice(LANGUAGE_KEYS),
                    default="python",
                )
                config["spec"]["language"] = language  # type: ignore[index]

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
    current_tool = artifact_manager.get_current_tool()

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
    """Get the builder class for a given tool."""
    from promptosaurus.builders.cline import ClineBuilder
    from promptosaurus.builders.copilot import CopilotBuilder
    from promptosaurus.builders.cursor import CursorBuilder
    from promptosaurus.builders.kilo_cli import KiloCLIBuilder
    from promptosaurus.builders.kilo_ide import KiloIDEBuilder

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
