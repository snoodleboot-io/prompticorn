"""`prompticorn verify` (PRO-115).

The exit codes are a contract — CI pipelines branch on these numbers — so they
are asserted as values rather than as "non-zero".

Two of these are worth reading twice. `test_a_rogue_file_is_caught` is the
reason check 2 exists at all: a verifier that only walked the lock's own list
would pass that tree. And `test_tampering_never_returns_click_s_exit_code`
pins the decision that the highest-severity signal must not be confusable with
a mistyped flag.
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


def test_a_clean_tree_verifies(project) -> None:
    built(project)

    result = run("verify")

    assert result.exit_code == ExitCode.CLEAN, result.output
    assert "nothing extra" in result.output


def test_a_hand_edited_output_fails_and_names_the_file(project) -> None:
    built(project)
    edited = project / "CLAUDE.md"
    edited.write_text(edited.read_text(encoding="utf-8") + "\nhand edit\n", encoding="utf-8")

    result = run("verify")

    assert result.exit_code == ExitCode.TAMPERED, result.output
    assert "CLAUDE.md" in result.output


def test_tampering_never_returns_click_s_exit_code(project) -> None:
    """2 is click's for usage errors. A supply-chain signal that fires on a
    typo is one people learn to ignore."""
    built(project)
    edited = project / "CLAUDE.md"
    edited.write_text("clobbered\n", encoding="utf-8")

    assert run("verify").exit_code != 2
    assert run("--nonexistent-flag").exit_code == 2


def test_a_rogue_file_is_caught(project) -> None:
    """The check that makes verification worth running: nothing in the
    generated roots may exist that the lock does not know about."""
    built(project)
    (project / ".claude" / "agents" / "rogue-agent.md").write_text("# Rogue\n", encoding="utf-8")

    result = run("verify")

    assert result.exit_code == ExitCode.DRIFT, result.output
    assert "rogue-agent.md" in result.output


def test_a_deleted_output_fails_and_names_it(project) -> None:
    built(project)
    (project / "CLAUDE.md").unlink()

    result = run("verify")

    assert result.exit_code == ExitCode.DRIFT, result.output
    assert "CLAUDE.md" in result.output


def test_hand_maintained_files_are_not_reported(project) -> None:
    """A team's own files sit outside the generated roots and are none of our
    business — reporting them would make the command unusable in a real repo."""
    built(project)
    (project / "README.md").write_text("hand-maintained\n", encoding="utf-8")
    (project / "src").mkdir()
    (project / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")

    assert run("verify").exit_code == ExitCode.CLEAN


def test_a_missing_lock_is_unusable_not_clean(project) -> None:
    """Exiting 0 with no lock would let a pipeline 'verify' nothing at all."""
    run("build")

    result = run("verify")

    assert result.exit_code == ExitCode.UNUSABLE_LOCK, result.output


def test_a_corrupt_lock_is_unusable(project) -> None:
    built(project)
    (project / ".prompticorn" / "prompticorn.lock").write_text(": not a lock\n", encoding="utf-8")

    assert run("verify").exit_code == ExitCode.UNUSABLE_LOCK


def test_verify_writes_nothing(project) -> None:
    """It is a check, not a fixer. A verify that repaired what it found would
    make the next run pass for the wrong reason."""
    built(project)
    before = {
        path: path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }

    run("verify")

    after = {
        path: path.read_bytes()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }
    assert after == before


def test_a_rebuild_still_verifies(project) -> None:
    """Regeneration must be a no-op against the lock, or the source/generated
    wall does not hold."""
    built(project)

    run("build")

    assert run("verify").exit_code == ExitCode.CLEAN


def test_every_finding_is_reported_not_just_the_first(project) -> None:
    """Reporting one of three problems turns one fix into three runs."""
    built(project)
    (project / "CLAUDE.md").unlink()
    (project / ".claude" / "agents" / "rogue-agent.md").write_text("# Rogue\n", encoding="utf-8")

    result = run("verify")

    assert "CLAUDE.md" in result.output
    assert "rogue-agent.md" in result.output
