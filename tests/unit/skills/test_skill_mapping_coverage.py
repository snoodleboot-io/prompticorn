"""Skill-reachability invariants for the mapping registries (PRO-7).

A skill only reaches a build if some agent or language references it. A skill
that sits on disk unreferenced is invisible — it costs maintenance and ships to
nobody. The inverse is worse: a mapping that names a skill with no file on disk
resolves to nothing at build time.

These tests pin both directions so the registries and the skills directory
cannot silently drift apart again.
"""

from pathlib import Path

import pytest
import yaml


def _mapped_skills(project_root: Path) -> set[str]:
    """Union every skill referenced by either mapping registry.

    Agent-level and language-level skills are unioned at build time (PRO-62),
    so reachability must be judged against both files together.
    """
    configurations = project_root / "prompticorn" / "configurations"
    mapped: set[str] = set()
    for name in ("agent_skill_mapping.yaml", "language_skill_mapping.yaml"):
        registry = yaml.safe_load((configurations / name).read_text(encoding="utf-8"))
        for entry in registry.values():
            if isinstance(entry, dict):
                mapped.update(entry.get("skills") or [])
    return mapped


def _skills_on_disk(skills_dir: Path) -> set[str]:
    return {path.name for path in skills_dir.iterdir() if path.is_dir()}


@pytest.mark.unit
class TestSkillMappingCoverage:
    """Every skill is reachable, and every mapping resolves."""

    def test_no_orphaned_skills(self, project_root, skills_dir):
        """Every skill on disk is referenced by at least one agent or language."""
        orphans = sorted(_skills_on_disk(skills_dir) - _mapped_skills(project_root))
        assert not orphans, (
            "These skills exist on disk but no agent or language maps them, so "
            "they never reach a build. Map them in agent_skill_mapping.yaml (or "
            f"language_skill_mapping.yaml), or delete them: {orphans}"
        )

    def test_no_mappings_without_a_skill_directory(self, project_root, skills_dir):
        """Every mapped skill name has a matching directory on disk."""
        dangling = sorted(_mapped_skills(project_root) - _skills_on_disk(skills_dir))
        assert not dangling, (
            "These skill names are mapped but have no directory under "
            f"prompticorn/skills/, so they resolve to nothing at build time: {dangling}"
        )
