"""`prompticorn lock` and `prompticorn build [--frozen]` (PRO-111).

The exit codes are a contract — CI pipelines branch on these numbers, so
changing one breaks every script that reads it. They are asserted as values
rather than as "non-zero".
"""

import re

import pytest
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.lockfile import ExitCode, LockReader

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


def lock_path(project):
    return project / ".prompticorn" / "prompticorn.lock"


# ── lock ───────────────────────────────────────────────────────────────────────


def test_lock_writes_a_lock(project) -> None:
    result = run("lock")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert lock_path(project).is_file()


def test_lock_records_units_and_outputs(project) -> None:
    run("build")
    run("lock")

    lock = LockReader.read(lock_path(project))
    assert len(lock.units) > 100, "the bundled tree should be recorded"
    assert lock.manifest_digest is not None


def test_locking_twice_leaves_the_file_byte_identical(project) -> None:
    """The property PRO-110 was built for, now reachable from the CLI."""
    run("lock")
    first = lock_path(project).read_bytes()

    result = run("lock")

    assert result.exit_code == ExitCode.CLEAN
    assert lock_path(project).read_bytes() == first
    assert "already up to date" in result.output


def test_lock_reports_an_unusable_lock(project) -> None:
    lock_path(project).parent.mkdir(exist_ok=True)
    lock_path(project).write_text("not: [valid", encoding="utf-8")

    result = run("lock")

    assert result.exit_code == ExitCode.UNUSABLE_LOCK


def test_lock_without_a_config_aborts(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert run("lock").exit_code != ExitCode.CLEAN


# ── build ──────────────────────────────────────────────────────────────────────


def test_build_generates_output(project) -> None:
    result = run("build")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert (project / "CLAUDE.md").is_file()
    assert (project / ".claude").is_dir()


def test_build_without_a_lock_still_builds_and_hints(project) -> None:
    """AC 3: no lock is not an error — refusing would make the feature a tax."""
    result = run("build")

    assert result.exit_code == ExitCode.CLEAN
    assert (project / "CLAUDE.md").is_file()
    assert "prompticorn lock" in result.output


def test_build_is_clean_against_a_fresh_lock(project) -> None:
    run("build")
    run("lock")

    result = run("build")

    assert result.exit_code == ExitCode.CLEAN
    assert "No drift" in result.output


def test_build_does_not_change_the_selected_tool(project) -> None:
    """Unlike `switch`, which is the command that does that."""
    run("build")

    assert "ai_tool: claude" in (project / ".prompticorn" / ".prompticorn.yaml").read_text()


def test_build_without_a_selected_tool_aborts(project) -> None:
    manifest = project / ".prompticorn" / ".prompticorn.yaml"
    manifest.write_text(MANIFEST.replace("ai_tool: claude\n", ""), encoding="utf-8")

    result = run("build")

    assert result.exit_code != ExitCode.CLEAN
    assert "switch" in result.output


# ── --frozen ───────────────────────────────────────────────────────────────────


def test_frozen_exits_non_zero_on_drift(project) -> None:
    """AC 2, first half."""
    run("build")
    run("lock")
    _dirty_the_manifest(project)

    result = run("build", "--frozen")

    assert result.exit_code == ExitCode.DRIFT
    assert "Frozen build" in result.output


def test_frozen_does_not_rewrite_the_lock(project) -> None:
    """The whole point of the flag.

    A frozen build that re-locked would report drift once and never again.
    """
    run("build")
    run("lock")
    before = lock_path(project).read_bytes()
    _dirty_the_manifest(project)

    run("build", "--frozen")

    assert lock_path(project).read_bytes() == before


def test_plain_build_re_resolves_and_rewrites_the_lock(project) -> None:
    """AC 2, second half — the behaviour --frozen exists to suppress."""
    run("build")
    run("lock")
    before = lock_path(project).read_bytes()
    _dirty_the_manifest(project)

    result = run("build")

    assert result.exit_code == ExitCode.CLEAN
    assert lock_path(project).read_bytes() != before


def test_frozen_names_the_drift_kind(project) -> None:
    run("build")
    run("lock")
    _dirty_the_manifest(project)

    result = run("build", "--frozen")

    assert "The manifest changed since the lock was written" in result.output


def test_frozen_reports_an_unusable_lock_distinctly(project) -> None:
    """AC 4: 3 is not 1. A corrupt lock is not the same as drift."""
    run("build")
    lock_path(project).write_text("not: [valid", encoding="utf-8")

    result = run("build", "--frozen")

    assert result.exit_code == ExitCode.UNUSABLE_LOCK


def test_a_lock_from_the_future_is_unusable_not_drift(project) -> None:
    run("build")
    run("lock")
    path = lock_path(project)
    path.write_text(
        re.sub(r"lock_version: '[^']+'", "lock_version: '99.0'", path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

    result = run("build", "--frozen")

    assert result.exit_code == ExitCode.UNUSABLE_LOCK


# ── the exit-code contract ─────────────────────────────────────────────────────


def test_the_documented_exit_codes() -> None:
    """AC 4: these are the numbers scripts branch on."""
    assert ExitCode.CLEAN == 0
    assert ExitCode.DRIFT == 1
    assert ExitCode.UNUSABLE_LOCK == 3


def test_unusable_lock_avoids_clicks_usage_code() -> None:
    """`click` uses 2 for usage errors.

    Reusing it would make "you typed the command wrong" indistinguishable from
    "the lock is corrupt" in any script that checks.
    """
    assert ExitCode.UNUSABLE_LOCK != 2


def test_every_exit_code_is_documented() -> None:
    for code in ExitCode:
        assert code.meaning


@pytest.mark.parametrize("command", ["lock", "build"])
def test_the_help_documents_the_exit_codes(command: str) -> None:
    result = run(command, "--help")

    assert "Exit codes" in result.output


def _dirty_the_manifest(project) -> None:
    manifest = project / ".prompticorn" / ".prompticorn.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8") + "\n# an edit the lock has not seen\n",
        encoding="utf-8",
    )
