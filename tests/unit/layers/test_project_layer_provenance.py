"""What a generated file says about which layer it came from (PRO-165).

`layer` is documented as "which layer won". While the bundled library was the only
possible answer, a per-build constant said it correctly by accident. With a layer
stack it is a per-unit fact, and the constant made one build contradict itself:
`.prompticorn/provenance.json` recorded `layer: builtin` for a unit whose entry in
`prompticorn.lock`, written by the same command, recorded `layer: project`.

Driven through the real CLI, and asserted against the sidecar and the inline
header together, because those are the two places anyone reads provenance from and
they are produced by different code paths in the same pass.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.content.content_resolver import default_resolver
from prompticorn.content.content_unit import BUILTIN_LAYER
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.unit_id import UnitId
from prompticorn.layers import PROJECT_LAYER
from prompticorn.lockfile import ExitCode
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.provenance import UNVERSIONED, ProvenanceHeader
from prompticorn.store import store_paths

MARKER = "Prompticorn override marker."

# Two kinds whose emitted file is attributed to the unit it came from, so the
# layer recorded for that file is the layer that won for that unit. (Claude's
# workflow and subagent documents are attributed to their PARENT agent, which is a
# separate inaccuracy in attribution rather than in layer, and is not what this
# pins.)
OVERRIDDEN = {
    "skill": (
        "skill/api-versioning-strategy/minimal",
        ".claude/skills/api-versioning-strategy/SKILL.md",
    ),
    "agent": ("agent/debug", ".claude/agents/debug-agent.md"),
}

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
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(
        yaml.safe_dump(MANIFEST), encoding="utf-8"
    )
    monkeypatch.chdir(root)
    return root


@pytest.fixture(params=sorted(OVERRIDDEN), ids=sorted(OVERRIDDEN))
def overridden(request, project: Path) -> tuple[str, str]:
    """Write a project override of one unit and return (unit id, emitted path)."""
    unit, emitted = OVERRIDDEN[request.param]
    unit_id = UnitId.parse(unit)
    layer = DirectoryContentSource(root=project / ".prompticorn" / "content", layer=PROJECT_LAYER)
    destination = layer.path_for(unit_id)
    assert destination is not None
    destination.parent.mkdir(parents=True, exist_ok=True)
    bundled = default_resolver().read(unit_id)
    destination.write_text(f"{bundled.rstrip()}\n\n{MARKER}\n", encoding="utf-8")
    return unit, emitted


def sidecar(project: Path) -> dict:
    return json.loads((project / ".prompticorn" / "provenance.json").read_text(encoding="utf-8"))


class TestAnOverriddenUnit:
    def test_the_sidecar_records_the_layer_that_won(self, project: Path, overridden):
        unit, emitted = overridden

        assert run("build").exit_code == ExitCode.CLEAN

        assert sidecar(project)[emitted]["layer"] == PROJECT_LAYER

    def test_the_inline_header_records_the_layer_that_won(self, project: Path, overridden):
        """The sidecar and the header are written by the same pass but rendered by
        different code; a reader who opens the file sees only the header."""
        unit, emitted = overridden

        run("build")

        record = ProvenanceHeader.parse((project / emitted).read_text(encoding="utf-8"))
        assert record is not None
        assert record.layer == PROJECT_LAYER

    def test_the_version_is_not_the_bundled_package_version(self, project: Path, overridden):
        """A directory layer is a working tree, not a release. Stamping the
        package version would describe content that lost."""
        unit, emitted = overridden

        run("build")

        assert sidecar(project)[emitted]["version"] == UNVERSIONED

    def test_provenance_and_the_lock_agree_about_the_layer(self, project: Path, overridden):
        """The defect, stated directly: two records of "which layer won", written
        by the same command, that said different things."""
        unit, emitted = overridden
        run("build")

        run("lock")

        lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
        locked = {locked_unit.id.render(): locked_unit.layer for locked_unit in lock.units}
        assert sidecar(project)[emitted]["layer"] == locked[unit]


class TestUnitsThatWereNotOverridden:
    def test_a_bundled_unit_in_the_same_build_still_says_builtin(self, project: Path, overridden):
        """The per-unit answer has to differ WITHIN one build, which is the thing a
        constant could not express however it was set."""
        _, emitted = overridden
        run("build")

        entries = sidecar(project)
        others = [
            path
            for path, record in entries.items()
            if path != emitted and record["unit"].startswith("skill/")
        ]
        assert others, "no other skill outputs to compare against"
        assert all(entries[path]["layer"] == BUILTIN_LAYER for path in others)

    def test_a_build_with_no_overrides_is_entirely_builtin(self, project: Path):
        """Guards the premise, and pins the pre-existing behaviour: every layer
        value in a project with no override directory must still be `builtin`."""
        run("build")

        assert {record["layer"] for record in sidecar(project).values()} == {BUILTIN_LAYER}
