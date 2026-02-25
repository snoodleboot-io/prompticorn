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

from promptcli import fill_registry
from promptcli.registry import MODES, MODE_FILES, ALWAYS_ON, PROMPTS_DIR, validate
from sweet_tea.factory import Factory


# ── Initialize registry ───────────────────────────────────────────────────────
# Register all builders with sweet_tea at module load time
fill_registry()


# ── Shared options ─────────────────────────────────────────────────────────────

output_option = click.option(
    "--output", "-o",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Directory to write output into. Defaults to current directory.",
)

dry_run_option = click.option(
    "--dry-run", "-n",
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
    """Build .kilocode/ for Kilo Code."""
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
        ("kilobuilder",    "Kilo Code"),
        ("clinebuilder",   "Cline"),
        ("cursorbuilder",  "Cursor"),
        ("copilotbuilder", "GitHub Copilot"),
    ]:
        _run_build(builder_key, label, output, dry_run)


# ── list ───────────────────────────────────────────────────────────────────────

@cli.command("list")
def list_prompts():
    """List all registered modes and their prompt files."""
    always_header = click.style("ALWAYS ON (all modes)", bold=True)
    click.echo(f"\n{always_header}")
    for fname in ALWAYS_ON:
        exists = "✓" if (PROMPTS_DIR / fname).exists() else click.style("✗ MISSING", fg="red")
        click.echo(f"  {exists}  {fname}")

    for mode_key, label in MODES.items():
        header = click.style(f"\n{label.upper()} MODE  [{mode_key}]", bold=True)
        click.echo(header)
        files = MODE_FILES.get(mode_key, [])
        if not files:
            click.secho("  (no files registered)", fg="yellow")
            continue
        for fname in files:
            exists = "✓" if (PROMPTS_DIR / fname).exists() else click.style("✗ MISSING", fg="red")
            click.echo(f"  {exists}  {fname}")

    click.echo()


# ── validate ───────────────────────────────────────────────────────────────────

@cli.command("validate")
def validate_prompts():
    """
    Check that all registered prompt files exist and no files in prompts/
    are unregistered (orphans).
    """
    click.echo("\n▶ Validating prompt registry...\n")
    errors = validate()
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
