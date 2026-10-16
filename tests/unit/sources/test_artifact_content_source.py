"""`ArtifactContentSource` against the ContentSource contract (PRO-117).

This suite should have existed from PRO-124. It did not, and the gap hid a real
defect: `BuiltinContentSource.units()` stamped every unit with the literal
``builtin`` layer instead of the source's own name, so a subclass that renamed
itself still reported everything it served as bundled content. The lock would
have recorded content fetched from an artifact as coming from the package.

The contract's `test_every_unit_declares_the_sources_layer` is precisely the
check that catches it — it just had never been pointed at a subclass.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompticorn.sources.artifact_content_source import ArtifactContentSource
from tests.unit.content.content_source_contract import ContentSourceContract


def populate(root: Path) -> Path:
    skill = root / "skills" / "testing-strategies" / "minimal"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Testing Strategies\n", encoding="utf-8")
    core = root / "agents" / "core"
    core.mkdir(parents=True)
    (core / "system.md").write_text("# System\n", encoding="utf-8")
    return root


class TestContract(ContentSourceContract):
    @pytest.fixture
    def source(self, tmp_path: Path) -> ArtifactContentSource:
        return ArtifactContentSource(root=populate(tmp_path / "artifact"), layer="local/house@1.0.0")


def test_units_carry_the_artifact_layer_not_builtin(tmp_path: Path):
    """The defect, stated directly."""
    source = ArtifactContentSource(root=populate(tmp_path / "artifact"), layer="local/house@1.0.0")

    assert {unit.layer for unit in source.units()} == {"local/house@1.0.0"}
