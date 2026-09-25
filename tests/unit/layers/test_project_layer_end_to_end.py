"""A project override, all the way to the files a tool reads (PRO-117).

Through the real CLI. The unit tests prove the stack resolves the right winner;
these prove the winner is what `build` writes, what `lock` records, and what
`verify` accepts — which is the only sense in which an override "works".

**Parametrised over every unit kind, and that is the point** (PRO-165). The first
version of this suite covered `skill` alone, and passed, while `workflow` and
`subagent` were resolving from the installed package directory and ignoring the
layer stack entirely — writing bundled text into the output while the lock
recorded the override's digest under `layer: project`, with `verify` calling the
pair clean. One kind's worth of coverage cannot see that; five kinds' can, and
the two that were broken fail every case below before the conversion.

The override is the bundled text plus a marker line, for each kind. Constructed
that way rather than written by hand because it is what an override *is* — an
edit to shipped content — and because it keeps the generated output otherwise
valid, so a failure means the layer was ignored rather than that the replacement
text was unusable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.content.content_resolver import default_resolver
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.unit_id import UnitId
from prompticorn.layers import PROJECT_LAYER
from prompticorn.lockfile import ExitCode
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.store import store_paths

MARKER = "Never version by header."

MANIFEST = {
    "version": "2.0",
    "repository": {"type": "single-language"},
    "spec": {"language": "python"},
    "variant": "minimal",
    "active_personas": ["software_engineer"],
    "ai_tool": "claude",
}


@dataclass(frozen=True)
class Kind:
    """One unit kind, and the file a project override of it must reach.

    Attributes:
        unit: The unit id to override.
        emitted: The generated file, relative to the project root, whose text
            must carry the override.
    """

    unit: str
    emitted: str

    @property
    def unit_id(self) -> UnitId:
        return UnitId.parse(self.unit)


# One per UnitKind. `agent` is authored without a variant; the rest are addressed
# by one, which is why the ids below are not uniform.
KINDS = {
    "skill": Kind(
        unit="skill/api-versioning-strategy/minimal",
        emitted=".claude/skills/api-versioning-strategy/SKILL.md",
    ),
    "agent": Kind(unit="agent/debug", emitted=".claude/agents/debug-agent.md"),
    "convention": Kind(
        unit="convention/core/system",
        emitted=".claude/conventions/core/general.md",
    ),
    "workflow": Kind(unit="workflow/code/minimal", emitted=".claude/workflows/code.md"),
    "subagent": Kind(
        unit="subagent/debug/root-cause/minimal",
        emitted=".claude/subagents/root-cause.md",
    ),
}


def run(*args):
    return CliRunner().invoke(cli, list(args))


@pytest.fixture(params=sorted(KINDS), ids=sorted(KINDS))
def kind(request) -> Kind:
    return KINDS[request.param]


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    monkeypatch.delenv("PROMPTICORN_USER_LAYER", raising=False)
    root = tmp_path / "project"
    (root / ".prompticorn").mkdir(parents=True)
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(
        yaml.safe_dump(MANIFEST), encoding="utf-8"
    )
    monkeypatch.chdir(root)
    return root


def content_root(project: Path) -> Path:
    return project / ".prompticorn" / "content"


def add_override(project: Path, kind: Kind) -> None:
    """Write the bundled text plus the marker into the project layer.

    The destination path comes from the layer's own ID-to-path mapping rather
    than being spelled out per kind: the project layer uses the bundled layout,
    so asking the source where a unit lives is the same question the build will
    ask, and a test that hard-coded the paths could pass against a mapping the
    build does not agree with.
    """
    layer = DirectoryContentSource(root=content_root(project), layer=PROJECT_LAYER)
    destination = layer.path_for(kind.unit_id)
    assert destination is not None, f"no path mapping for {kind.unit}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    bundled = default_resolver().read(kind.unit_id)
    destination.write_text(f"{bundled.rstrip()}\n\n{MARKER}\n", encoding="utf-8")


def emitted_text(project: Path, kind: Kind) -> str:
    path = project / kind.emitted
    assert path.is_file(), f"build wrote no {kind.emitted}"
    return path.read_text(encoding="utf-8")


class TestTheOverrideReachesTheOutput:
    def test_build_writes_the_project_override(self, project: Path, kind: Kind):
        add_override(project, kind)

        result = run("build")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert MARKER in emitted_text(project, kind)

    def test_without_an_override_the_bundled_unit_is_written(self, project: Path, kind: Kind):
        """Guards the premise: the marker must not already be in bundled content,
        or every assertion above would hold for a build that ignored the layer."""
        run("build")

        assert MARKER not in emitted_text(project, kind)

    def test_lock_records_that_the_project_layer_won(self, project: Path, kind: Kind):
        add_override(project, kind)
        run("build")

        run("lock")

        lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
        winners = {unit.id.render(): unit.layer for unit in lock.units}
        assert winners[kind.unit] == PROJECT_LAYER

    def test_the_lock_and_the_output_agree(self, project: Path, kind: Kind):
        """The contradiction this suite exists to catch. A build that resolved
        from the package while the lock resolved through the stack satisfies each
        of the two tests above and is still wrong — the lock claims the project
        layer won and the file on disk is bundled text."""
        add_override(project, kind)
        run("build")
        run("lock")

        lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
        winners = {unit.id.render(): unit.layer for unit in lock.units}
        assert winners[kind.unit] == PROJECT_LAYER
        assert MARKER in emitted_text(project, kind)

    def test_an_overridden_build_verifies_clean(self, project: Path, kind: Kind):
        """Build, lock and verify must resolve through the same layers, or the
        override would read as a hand edit."""
        add_override(project, kind)
        run("build")
        run("lock")

        assert run("verify").exit_code == ExitCode.CLEAN

    def test_regenerate_reproduces_the_override(self, project: Path, kind: Kind):
        add_override(project, kind)
        run("build")
        run("lock")
        (project / kind.emitted).write_text("clobbered\n", encoding="utf-8")

        result = run("regenerate")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert MARKER in emitted_text(project, kind)


class TestIsolation:
    def test_a_command_does_not_leak_its_layers_into_the_next(self, project: Path, kind: Kind):
        """The CLI installs a project resolver for one command and must put the
        default back, or a later invocation in the same process would read the
        previous project's overrides."""
        add_override(project, kind)
        run("build")

        assert not any(unit.layer == PROJECT_LAYER for unit in default_resolver().units())

    def test_a_user_directory_does_not_affect_the_build_by_default(self, project: Path, tmp_path):
        """Machine-local content must not change a committed lock."""
        user_skill = (
            tmp_path / "store" / "content" / "skills" / "api-versioning-strategy" / "minimal"
        )
        user_skill.mkdir(parents=True)
        (user_skill / "SKILL.md").write_text("# machine-local\n", encoding="utf-8")

        run("build")

        assert "machine-local" not in (project / KINDS["skill"].emitted).read_text(encoding="utf-8")


class TestAnEmptyContentDirectoryIsNotAnOverride:
    """Pinning behaviour that is already correct, because the obvious
    simplification of the presence check would break it: an existing but empty
    `.prompticorn/content/` must build exactly as a project with none."""

    def test_an_empty_content_directory_builds_clean(self, project: Path):
        content_root(project).mkdir(parents=True)

        result = run("build")

        assert result.exit_code == ExitCode.CLEAN, result.output

    def test_an_empty_layer_produces_the_same_bytes_as_no_layer(self, project: Path, tmp_path):
        """Byte-compared rather than spot-checked: an empty layer that changed one
        emitted file would be a layer contributing content it does not have."""
        run("build")
        without = {
            path.relative_to(project).as_posix(): path.read_bytes()
            for path in sorted((project / ".claude").rglob("*"))
            if path.is_file()
        }

        content_root(project).mkdir(parents=True)
        run("build")
        with_empty_layer = {
            path.relative_to(project).as_posix(): path.read_bytes()
            for path in sorted((project / ".claude").rglob("*"))
            if path.is_file()
        }

        assert with_empty_layer == without

    def test_no_unit_is_attributed_to_the_project_layer(self, project: Path):
        content_root(project).mkdir(parents=True)
        run("build")

        run("lock")

        lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
        assert not [unit.id.render() for unit in lock.units if unit.layer == PROJECT_LAYER]
