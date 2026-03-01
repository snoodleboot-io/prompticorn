"""
cli.py
Click-based CLI for the prompt library.

Commands:
  prompt build kilo    [--output DIR] [--dry-run]
  prompt build cline   [--output DIR] [--dry-run]
  prompt build cursor  [--output DIR] [--dry-run]
  prompt build copilot [--output DIR] [--dry-run]
  prompt build all     [--output DIR] [--dry-run]
  prompt list
  prompt validate
"""

import sys
from typing import Any

import click

from promptcli.config import DEFAULT_CONFIG_TEMPLATE, ConfigHandler
from promptcli.questions.base.constants import (
    REPO_TYPE_MULTI_FOLDER,
    REPO_TYPE_SINGLE,
)
from promptcli.questions.base.repository_type_question import RepositoryTypeQuestion
from promptcli.questions.language import LANGUAGE_KEYS

# from promptcli import fill_registry
from promptcli.registry import registry

# # ── Initialize registry ───────────────────────────────────────────────────────
# fill_registry()


# ── Shared options ─────────────────────────────────────────────────────────────

output_option = click.option(
    "--output",
    "-o",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Directory to write output into. Defaults to current directory.",
)

dry_run_option = click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    default=False,
    help="Preview what would be written without touching the filesystem.",
)


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

    Walks through questions to set up .prompty/configurations.yaml with
    your language, runtime, package manager, testing framework, and more.
    """

    from promptcli.ui._selector import select_option_with_explain

    click.echo("\n" + "=" * 60)
    click.secho("  Prompt CLI Initialization", bold=True, fg="cyan")
    click.echo("=" * 60)
    click.echo("\nUse ↑/↓ arrows, numbers, or Enter for defaults.")

    # Step 1: Repository type
    repo_question = RepositoryTypeQuestion()
    default_idx = repo_question.options.index(repo_question.default)

    click.echo(f"\n{repo_question.question_text}\n")
    click.echo(repo_question.explanation)
    click.echo("\n[?] Press ? to see option explanations, Enter to continue...")
    repo_type = select_option_with_explain(
        question=repo_question.question_text,
        options=repo_question.options,
        explanations=repo_question.option_explanations,
        question_explanation=repo_question.explanation,
        default_index=default_idx,
    )

    # Step 2 & 3: Handle language questions based on repo type
    # Use isinstance() for proper type narrowing from str | list[str] to str
    if isinstance(repo_type, str) and repo_type == REPO_TYPE_SINGLE:
        from promptcli.questions.handlers.handle_single_language_questions import (
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
            config["defaults"]["language"] = language  # type: ignore[index]

    # Save configuration
    ConfigHandler.save_config(config)

    click.echo("\n\n" + "=" * 60)
    click.secho("  Configuration saved!", bold=True, fg="green")
    click.echo("=" * 60)
    click.echo(f"\n  Config file: {ConfigHandler.get_config_path()}")
    click.echo("\n  You can now run:")
    click.echo("    prompt build <target>")
    click.echo("\n  Or edit the config file directly to customize.\n")


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
