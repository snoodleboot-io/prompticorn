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
from pathlib import Path

import click
from sweet_tea.factory import Factory

from promptcli import fill_registry
from promptcli.registry import registry

# ── Initialize registry ───────────────────────────────────────────────────────
fill_registry()


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
    Prompt library CLI — build AI coding assistant configs from your prompt files.

    Edit files in prompts/, then run `prompt build <target>` to generate
    the right config for Kilo Code, Cline, Cursor, or GitHub Copilot.
    """


# ── build group ───────────────────────────────────────────────────────────────


@cli.group()
def build():
    """Build output configs for a specific tool."""


def _run_build(builder_key: str, target_label: str, output: str, dry_run: bool):
    out = Path(output).resolve()
    tag = "[dry-run] " if dry_run else ""
    click.echo(f"\n▶ {tag}Building {target_label} → {out}\n")
    try:
        builder = Factory.create(builder_key, library="promptcli")
        actions = builder.build(out, dry_run=dry_run)
    except FileNotFoundError as e:
        click.secho(f"  ✗ {e}", fg="red", err=True)
        sys.exit(1)
    for action in actions:
        color = "yellow" if action.startswith("[dry-run]") else "green"
        click.secho(f"  {action}", fg=color)
    click.echo()
    if dry_run:
        click.secho("  (dry run — nothing written)", fg="yellow")


@build.command("kilo")
@output_option
@dry_run_option
def build_kilo(output, dry_run):
    """Build .kilo/ for Kilo Code."""
    _run_build("kilobuilder", "Kilo Code", output, dry_run)


@build.command("cline")
@output_option
@dry_run_option
def build_cline(output, dry_run):
    """Build .clinerules for Cline."""
    _run_build("clinebuilder", "Cline", output, dry_run)


@build.command("cursor")
@output_option
@dry_run_option
def build_cursor(output, dry_run):
    """Build .cursor/rules/ and .cursorrules for Cursor."""
    _run_build("cursorbuilder", "Cursor", output, dry_run)


@build.command("copilot")
@output_option
@dry_run_option
def build_copilot(output, dry_run):
    """Build .github/copilot-instructions.md and per-mode instruction files."""
    _run_build("copilotbuilder", "GitHub Copilot", output, dry_run)


@build.command("all")
@output_option
@dry_run_option
def build_all(output, dry_run):
    """Build all targets: Kilo, Cline, Cursor, and Copilot."""
    for builder_key, label in [
        ("kilobuilder", "Kilo Code"),
        ("clinebuilder", "Cline"),
        ("cursorbuilder", "Cursor"),
        ("copilotbuilder", "GitHub Copilot"),
    ]:
        _run_build(builder_key, label, output, dry_run)


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
    from promptcli.config import DEFAULT_CONFIG_TEMPLATE, ConfigHandler, create_default_config
    from promptcli.questions import (
        LANGUAGE_KEYS,
        REPO_TYPE_MULTI_FOLDER,
        REPO_TYPE_SINGLE,
        RepositoryTypeQuestion,
        get_language_questions,
    )

    click.echo("\n" + "=" * 60)
    click.secho("  Prompt CLI Initialization", bold=True, fg="cyan")
    click.echo("=" * 60)
    click.echo("\nThis wizard will help you configure prompt conventions.")
    click.echo("Press Enter to accept defaults shown in brackets.\n")

    # Step 1: Repository type
    repo_question = RepositoryTypeQuestion()
    click.echo(f"\n{repo_question.question_text}\n")
    click.echo(repo_question.explanation)
    click.echo("\nOptions:")
    for opt in repo_question.options:
        explanation = repo_question.option_explanations.get(opt, "")
        is_default = " [default]" if opt == repo_question.default else ""
        click.echo(f"  {opt:30s} - {explanation}{is_default}")

    repo_type = click.prompt(
        "\nRepository type",
        type=click.Choice(repo_question.options),
        default=repo_question.default,
    )

    # Step 2: Language (only for single-language repos)
    language = ""
    if repo_type == REPO_TYPE_SINGLE:
        click.echo("\n\nAvailable languages:")
        for lang in sorted(LANGUAGE_KEYS):
            click.echo(f"  - {lang}")

        language = click.prompt(
            "\nPrimary language",
            type=click.Choice(LANGUAGE_KEYS),
            default="python",
        )

        # Step 3: Language-specific questions
        lang_questions = get_language_questions(language)
        config = create_default_config(language, repo_type=repo_type)

        for q in lang_questions:
            click.echo(f"\n\n{q.question_text}\n")
            click.echo(q.explanation)
            click.echo("\nOptions:")
            for opt in q.options:
                explanation = q.option_explanations.get(opt, "")
                is_default = " [default]" if opt == q.default else ""
                click.echo(f"  {opt:30s} - {explanation}{is_default}")

            # Store key without language prefix for config
            config_key = q.key.replace(f"{language}_", "")
            value = click.prompt(
                f"\n{q.question_text().split('?')[0]}",
                type=click.Choice(q.options),
                default=q.default,
            )
            config["defaults"][config_key] = value
    else:
        # Multi-folder or mixed - just save repo type for now
        config = DEFAULT_CONFIG_TEMPLATE.copy()
        config["repository"]["type"] = repo_type
        if repo_type == REPO_TYPE_MULTI_FOLDER:
            click.echo("\n\nFolder mappings will be configured in a future step.")
            click.echo("For now, set up your primary language:")
            language = click.prompt(
                "\nPrimary language",
                type=click.Choice(LANGUAGE_KEYS),
                default="python",
            )
            config["defaults"]["language"] = language

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
    errors = registry.validate()
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
