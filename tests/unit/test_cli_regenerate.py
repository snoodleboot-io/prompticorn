"""`prompticorn regenerate` (PRO-116).

The command that makes generated output disposable. Its whole value is that a
tree in any state — hand-patched, half-deleted, salted with a rogue agent —
comes back to exactly what the lock describes, so most of these tests damage a
tree in a specific way and then assert it is byte-identical to where it started.

Two are load-bearing beyond that. `test_the_lock_is_never_written` pins the
property that separates this from `build`: no re-resolution, on any path,
including the failing ones. And `test_moved_sources_are_refused_and_nothing_is_
touched` pins the refusal — rebuilding from sources the lock does not describe
would produce a tree nobody asked for, and doing it after deleting the old one
would leave no way back.
"""

import pytest
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.lockfile import ExitCode

MANIFEST = """\
version: '2.0'
repository:
  type: single-language
spec:
  language: python
variant: minimal
active_personas:
  - software_engineer
ai_tool: claude
"""


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A scratch project with a manifest and a selected tool."""
    config_dir = tmp_path / ".prompticorn"
    config_dir.mkdir()
    (config_dir / ".prompticorn.yaml").write_text(MANIFEST, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run(*args):
    return CliRunner().invoke(cli, list(args))


def built(project):
    """A project that has been built and locked — the clean starting point."""
    run("build")
    run("lock")
    return project


def snapshot(project) -> dict[str, bytes]:
    """Every file in the tree, keyed by POSIX-relative path."""
    return {
        path.relative_to(project).as_posix(): path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


def test_a_clean_tree_regenerates_to_itself(project) -> None:
    """The base case, and the one the CI matrix depends on: regenerating an
    untouched tree reproduces it byte for byte."""
    built(project)
    before = snapshot(project)

    result = run("regenerate")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert snapshot(project) == before


def test_a_hand_edited_output_is_restored(project) -> None:
    """The documented answer to a hand-patch: recompile, don't edit."""
    built(project)
    before = snapshot(project)
    edited = project / "CLAUDE.md"
    edited.write_text(edited.read_text(encoding="utf-8") + "\nhand edit\n", encoding="utf-8")

    result = run("regenerate")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert snapshot(project) == before
    assert run("verify").exit_code == ExitCode.CLEAN


def test_a_rogue_file_is_removed(project) -> None:
    """A rebuild alone would leave it: nothing overwrites a file no builder
    writes. Wiping the generated roots first is what makes this work."""
    built(project)
    before = snapshot(project)
    (project / ".claude" / "agents" / "rogue-agent.md").write_text("# Rogue\n", encoding="utf-8")

    result = run("regenerate")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert snapshot(project) == before


def test_a_deleted_output_is_restored(project) -> None:
    built(project)
    before = snapshot(project)
    (project / "CLAUDE.md").unlink()

    result = run("regenerate")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert snapshot(project) == before


def test_a_wholly_deleted_tree_is_restored(project) -> None:
    """Generated directories are disposable. Deleting one has to be recoverable,
    or that claim is just words in a document."""
    import shutil

    built(project)
    before = snapshot(project)
    shutil.rmtree(project / ".claude")
    (project / "CLAUDE.md").unlink()

    result = run("regenerate")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert snapshot(project) == before


def test_the_lock_is_never_written(project) -> None:
    """No re-resolution, on any path. A regenerate that re-locked would report
    success by moving the target, which is the failure `build --frozen` exists
    to prevent."""
    built(project)
    lock = project / ".prompticorn" / "prompticorn.lock"
    recorded = lock.read_bytes()
    (project / "CLAUDE.md").write_text("clobbered\n", encoding="utf-8")

    run("regenerate")

    assert lock.read_bytes() == recorded


def test_moved_sources_are_refused_and_nothing_is_touched(project) -> None:
    """Rebuilding from sources the lock does not describe would produce a tree
    nobody asked for — and doing it after wiping the old one leaves no way
    back. The refusal has to come before the wipe."""
    built(project)
    before = snapshot(project)
    manifest = project / ".prompticorn" / ".prompticorn.yaml"
    manifest.write_text(MANIFEST.replace("minimal", "verbose"), encoding="utf-8")

    result = run("regenerate")

    assert result.exit_code == ExitCode.DRIFT, result.output
    assert "Refusing to regenerate" in result.output
    assert snapshot(project) == {**before, ".prompticorn/.prompticorn.yaml": manifest.read_bytes()}


def test_the_refusal_names_what_moved(project) -> None:
    """"Refused" without a subject leaves the reader with nothing to fix."""
    built(project)
    manifest = project / ".prompticorn" / ".prompticorn.yaml"
    manifest.write_text(MANIFEST.replace("minimal", "verbose"), encoding="utf-8")

    result = run("regenerate")

    assert ".prompticorn.yaml" in result.output


def test_a_missing_lock_is_unusable(project) -> None:
    """There is nothing to regenerate *from*. Building anyway would make this
    an alias for `build`, which is the one thing it must not be."""
    run("build")

    result = run("regenerate")

    assert result.exit_code == ExitCode.UNUSABLE_LOCK, result.output
    assert "prompticorn lock" in result.output


def test_a_corrupt_lock_is_unusable(project) -> None:
    built(project)
    (project / ".prompticorn" / "prompticorn.lock").write_text(": not a lock\n", encoding="utf-8")

    assert run("regenerate").exit_code == ExitCode.UNUSABLE_LOCK


def test_regenerate_never_returns_click_s_exit_code(project) -> None:
    """2 is click's, for usage errors. Every documented code here avoids it."""
    built(project)
    (project / "CLAUDE.md").write_text("clobbered\n", encoding="utf-8")
    assert run("regenerate").exit_code != 2

    manifest = project / ".prompticorn" / ".prompticorn.yaml"
    manifest.write_text(MANIFEST.replace("minimal", "verbose"), encoding="utf-8")
    assert run("regenerate").exit_code != 2


def test_regenerating_twice_changes_nothing(project) -> None:
    """Idempotence is what makes it safe to put in a pre-commit hook."""
    built(project)
    run("regenerate")
    once = snapshot(project)

    run("regenerate")

    assert snapshot(project) == once
