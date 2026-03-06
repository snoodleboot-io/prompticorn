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

from promptosaurus.config_handler import DEFAULT_CONFIG_TEMPLATE, ConfigHandler
from promptosaurus.questions.base.constants import (
    REPO_TYPE_MULTI_FOLDER,
    REPO_TYPE_SINGLE,
)
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion
from promptosaurus.questions.language import LANGUAGE_KEYS

# from promptcli import fill_registry
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
