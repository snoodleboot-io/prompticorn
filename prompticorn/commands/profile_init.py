"""`prompticorn init --profile` (PRO-133).

The adoption path. A new repository set up correctly without anyone answering
twenty questions is the reason a team standard spreads at all — the interview is
worth doing once, not once per project.

The result must be indistinguishable from running `init` and giving the same
answers, so this writes the manifest through the same `ConfigHandler` path the
interview uses and then builds with the same builder. Nothing here reimplements
either; a second path would be free to drift from the first, and the drift would
show up as two projects that were supposed to match and do not.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from prompticorn.profiles import FileProfileStore, ProfileService


def run(profile_name: str, root: Path | None = None) -> int:
    """Configure ``root`` from a saved profile and generate its output.

    Args:
        profile_name: Which profile to apply.
        root: Project directory. Defaults to the working directory.

    Returns:
        A process exit code.
    """
    target = root if root is not None else Path(".")
    service = ProfileService(store=FileProfileStore())

    outcome = service.apply(profile_name, target)
    click.secho(f"\n✓ Configured from {outcome.profile}", fg="green")
    if outcome.had_existing and not outcome.changed_nothing:
        click.echo(f"\n{outcome.diff.render()}")

    tool = outcome.profile.payload.get("ai_tool")
    if not isinstance(tool, str) or not tool:
        click.echo("\n  The profile names no tool; run `prompticorn switch` to pick one.")
        return 0

    from prompticorn.prompt_builder import get_prompt_builder

    click.secho(f"\n  Generating {tool} configuration...", bold=True)
    for action in get_prompt_builder(tool).build(target, outcome.profile.payload, dry_run=False):
        click.echo(f"    {action}")

    click.secho("\n✓ Ready. Run `prompticorn lock` to record what this resolved to.", fg="green")
    return 0


def utc_now() -> str:
    """Current time in the one spelling the lock and the store share."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
