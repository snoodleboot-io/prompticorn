"""`prompticorn profile` (PRO-133).

Wiring and presentation only. Every command here delegates to
:class:`ProfileService` or :class:`ProfileTransfer`, which is what lets the
behaviour be tested without a terminal and keeps this file readable as a menu of
what the feature offers.

Two commands the ticket does not list are included: ``save`` and ``apply``.
PRO-132 built both as services and gave neither a way in, so without them the
milestone's headline feature is unreachable from the command line.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from prompticorn.profiles import (
    ConfigDiff,
    FileProfileStore,
    ProfileService,
    portable_payload,
)
from prompticorn.profiles.profile_transfer import ProfileTransfer


def _now() -> str:
    """Current time in the one spelling the lock and the store share."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _service() -> ProfileService:
    return ProfileService(store=FileProfileStore())


@click.group("profile")
def profile_group():
    """
    Capture a project's configuration and reproduce it elsewhere.

    A profile is the answer to "set this project up the way that one is". It
    holds the manifest — language, personas, variant, tool — under a name you
    choose, in `~/.prompticorn/profiles`.

    \b
    Saving never overwrites: each save is a new version, so comparing two of
    them is a real comparison and going back is a copy rather than a rebuild.

    \b
    Usage:
        prompticorn profile save backend --description "house standard"
        prompticorn profile apply backend
        prompticorn profile diff backend --repo
    """


@profile_group.command("list")
def list_profiles():
    """
    List saved profiles, newest version first.
    """
    store = FileProfileStore()
    names = store.names()
    if not names:
        click.echo(f"\n  No profiles in {store.root}.")
        click.echo("  Capture one with `prompticorn profile save <name>`.")
        return

    click.echo(f"\n  {len(names)} profile(s) in {store.root}:\n")
    for name in names:
        versions = store.versions_of(name)
        try:
            current = store.load(name)
            summary = current.description or "(no description)"
        except Exception:  # noqa: BLE001 - one unreadable profile must not hide the rest
            summary = "(unreadable)"
        click.echo(f"    {name}  v{versions[-1]}  {summary}")


@profile_group.command("show")
@click.argument("name")
@click.option("--version", type=int, default=None, help="Show this version instead of the newest.")
def show_profile(name: str, version: int | None):
    """
    Print a profile's contents.
    """
    profile = FileProfileStore().load(name, version)
    click.echo(f"\n  {profile}")
    if profile.description:
        click.echo(f"  {profile.description}")
    if profile.created_at:
        click.echo(f"  captured {profile.created_at}")
    click.echo(f"  digest {profile.digest()[:12]}…\n")
    click.echo(profile.canonical_text())


@profile_group.command("save")
@click.argument("name")
@click.option("--description", default="", help="Why this profile exists.")
def save_profile(name: str, description: str):
    """
    Capture this project's configuration as a new version of NAME.
    """
    profile = _service().save_from_repo(name, Path("."), description, _now())
    click.secho(f"\n✓ Saved {profile}", fg="green")


@profile_group.command("apply")
@click.argument("name")
@click.option("--version", type=int, default=None, help="Apply this version instead of the newest.")
@click.option("--dry-run", is_flag=True, help="Show what would change and write nothing.")
@click.option("--yes", is_flag=True, help="Do not ask before overwriting an existing manifest.")
def apply_profile(name: str, version: int | None, dry_run: bool, yes: bool):
    """
    Write a profile's configuration into this project.

    Overwriting an existing manifest asks first and shows the diff, because a
    configuration replaced without warning is one nobody can account for later.
    """
    service = _service()
    preview = service.apply(name, Path("."), version, dry_run=True)

    if preview.changed_nothing:
        click.echo(f"\n  {preview.render()}")
        return

    click.echo(f"\n{preview.diff.render()}")
    if dry_run:
        click.echo("\n  --dry-run: nothing written.")
        return
    if preview.had_existing and not yes:
        click.confirm("\n  Overwrite the existing manifest?", abort=True)

    outcome = service.apply(name, Path("."), version)
    click.secho(f"\n✓ Applied {outcome.profile}", fg="green")
    click.echo("  Run `prompticorn build` to regenerate from it.")


@profile_group.command("diff")
@click.argument("left")
@click.argument("right", required=False)
@click.option("--repo", is_flag=True, help="Compare LEFT against this project's manifest.")
def diff_profiles(left: str, right: str | None, repo: bool):
    """
    Compare two profiles, or a profile against this project.

    `diff <name> --repo` answers "how does this repo differ from our standard?",
    which is the question that actually gets asked.
    """
    store = FileProfileStore()

    if repo:
        from prompticorn.config_handler import ConfigHandler

        profile = store.load(left)
        config = ConfigHandler.load_config() if ConfigHandler.config_exists() else {}
        # Profile first: the question is how the repo differs *from the
        # standard*, so the standard is the baseline and the repo is the change.
        click.echo(f"\n  {profile} → this project\n")
        click.echo(ConfigDiff.between(profile.payload, portable_payload(config)).render())
        return

    if right is None:
        raise click.UsageError("give a second profile to compare, or pass --repo")

    one, two = store.load(left), store.load(right)
    click.echo(f"\n  {one} → {two}\n")
    click.echo(ConfigDiff.between(one.payload, two.payload).render())


@profile_group.command("export")
@click.argument("name")
@click.option(
    "--version", type=int, default=None, help="Export this version instead of the newest."
)
@click.option(
    "--output", "-o", required=True, type=click.Path(path_type=Path), help="Where to write it."
)
def export_profile(name: str, version: int | None, output: Path):
    """
    Write a profile to a file, so it can be committed or sent to someone.
    """
    profile = ProfileTransfer(store=FileProfileStore()).export(name, output, version)
    click.secho(f"\n✓ Exported {profile} to {output}", fg="green")


@profile_group.command("import")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--name", default=None, help="Store it under this name instead of the file's own.")
def import_profile(path: Path, name: str | None):
    """
    Read a profile file into the store as a new version.
    """
    profile = ProfileTransfer(store=FileProfileStore()).import_file(path, _now(), name)
    click.secho(f"\n✓ Imported {profile}", fg="green")


@profile_group.command("delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Do not ask for confirmation.")
def delete_profile(name: str, yes: bool):
    """
    Remove a profile and every version of it.
    """
    store = FileProfileStore()
    versions = store.versions_of(name)
    if not versions:
        click.secho(f"\n✗ No profile {name!r}.", fg="red", err=True)
        raise SystemExit(1)
    if not yes:
        click.confirm(f"\n  Delete {name!r} and its {len(versions)} version(s)?", abort=True)
    removed = store.delete(name)
    click.secho(f"\n✓ Deleted {name!r} ({removed} version(s))", fg="green")
