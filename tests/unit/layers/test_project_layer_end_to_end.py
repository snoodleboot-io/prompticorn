"""A project override, all the way to the files a tool reads (PRO-117).

Through the real CLI. The unit tests prove the stack resolves the right winner;
these prove the winner is what `build` writes, what `lock` records, and what
`verify` accepts — which is the only sense in which an override "works".
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.content.content_resolver import default_resolver
from prompticorn.lockfile import ExitCode
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.store import store_paths

OVERRIDE = "# API Versioning Strategy — our house rules\n\nNever version by header.\n"
UNIT = "skill/api-versioning-strategy/minimal"
EMITTED = ".claude/skills/api-versioning-strategy/SKILL.md"

MANIFEST = {
    "version": "2.0",
    "repository": {"type": "single-language"},
    "spec": {"language": "python"},
    "variant": "minimal",
    "active_personas": ["software_engineer"],
    "ai_tool": "claude",
}


def run(*args):
    return CliRunner().invoke(cli, list(args))


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    monkeypatch.delenv("PROMPTICORN_USER_LAYER", raising=False)
    root = tmp_path / "project"
    (root / ".prompticorn").mkdir(parents=True)
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(yaml.safe_dump(MANIFEST), encoding="utf-8")
    monkeypatch.chdir(root)
    return root


def add_override(project: Path) -> None:
    skill = project / ".prompticorn" / "content" / "skills" / "api-versioning-strategy" / "minimal"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(OVERRIDE, encoding="utf-8")


class TestTheOverrideReachesTheOutput:
    def test_build_writes_the_project_override(self, project: Path):
        add_override(project)

        result = run("build")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert "Never version by header." in (project / EMITTED).read_text(encoding="utf-8")

    def test_without_an_override_the_bundled_skill_is_written(self, project: Path):
        """Guards the premise: the text above must not be in the bundled skill."""
        run("build")

        assert "Never version by header." not in (project / EMITTED).read_text(encoding="utf-8")

    def test_lock_records_that_the_project_layer_won(self, project: Path):
        add_override(project)
        run("build")

        run("lock")

        lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
        winners = {unit.id.render(): unit.layer for unit in lock.units}
        assert winners[UNIT] == "project"

    def test_an_overridden_build_verifies_clean(self, project: Path):
        """Build, lock and verify must resolve through the same layers, or the
        override would read as a hand edit."""
        add_override(project)
        run("build")
        run("lock")

        assert run("verify").exit_code == ExitCode.CLEAN

    def test_regenerate_reproduces_the_override(self, project: Path):
        add_override(project)
        run("build")
        run("lock")
        (project / EMITTED).write_text("clobbered\n", encoding="utf-8")

        result = run("regenerate")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert "Never version by header." in (project / EMITTED).read_text(encoding="utf-8")


class TestIsolation:
    def test_a_command_does_not_leak_its_layers_into_the_next(self, project: Path, tmp_path, monkeypatch):
        """The CLI installs a project resolver for one command and must put the
        default back, or a later invocation in the same process would read the
        previous project's overrides."""
        add_override(project)
        run("build")

        assert not any(unit.layer == "project" for unit in default_resolver().units())

    def test_a_user_directory_does_not_affect_the_build_by_default(self, project: Path, tmp_path):
        """Machine-local content must not change a committed lock."""
        user_skill = tmp_path / "store" / "content" / "skills" / "api-versioning-strategy" / "minimal"
        user_skill.mkdir(parents=True)
        (user_skill / "SKILL.md").write_text("# machine-local\n", encoding="utf-8")

        run("build")

        assert "machine-local" not in (project / EMITTED).read_text(encoding="utf-8")
