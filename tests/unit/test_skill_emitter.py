"""Unit tests for the canonical SKILL.md emitter (PRO-32 / E2)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prompticorn.builders.skill_emitter import (
    AGENTS_SKILLS_BASE,
    skill_relative_path,
    write_skill,
)


class TestSkillEmitter(unittest.TestCase):
    """Verify the tool-agnostic Agent Skills SKILL.md writer."""

    def test_agents_skills_base_constant(self) -> None:
        self.assertEqual(AGENTS_SKILLS_BASE, ".agents")

    def test_relative_path_shape(self) -> None:
        self.assertEqual(
            skill_relative_path(".claude", "feature-planning"),
            ".claude/skills/feature-planning/SKILL.md",
        )
        self.assertEqual(
            skill_relative_path(AGENTS_SKILLS_BASE, "verify"),
            ".agents/skills/verify/SKILL.md",
        )

    def test_write_creates_file_and_returns_relative_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = write_skill(root, ".agents", "verify", "# Verify\n\n## Purpose\nCheck it.\n")
            self.assertEqual(rel, ".agents/skills/verify/SKILL.md")
            written = root / rel
            self.assertTrue(written.exists())
            # The emitter guarantees name/description frontmatter (PRO-7 follow-up);
            # the original body is preserved after the synthesized block.
            text = written.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nname: verify\n"))
            self.assertIn('description: "Check it."', text)
            self.assertIn("# Verify", text)

    def test_write_preserves_existing_frontmatter_verbatim(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "---\nname: s\ndescription: kept\n---\n\nbody\n"
            rel = write_skill(root, ".claude", "s", body)
            self.assertEqual((root / rel).read_text(encoding="utf-8"), body)

    def test_write_is_idempotent_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, ".claude", "s", "# A\n\n## Purpose\nFirst.\n")
            rel = write_skill(root, ".claude", "s", "# B\n\n## Purpose\nSecond.\n")
            self.assertIn("Second.", (root / rel).read_text(encoding="utf-8"))

    def test_folder_shape_matches_legacy_paths(self) -> None:
        """The relative paths equal what prompt_builder emitted per tool before."""
        cases = {
            ".kilo": ".kilo/skills/demo/SKILL.md",
            ".cline": ".cline/skills/demo/SKILL.md",
            ".claude": ".claude/skills/demo/SKILL.md",
            ".cursor": ".cursor/skills/demo/SKILL.md",
        }
        for base, expected in cases.items():
            self.assertEqual(skill_relative_path(base, "demo"), expected)


if __name__ == "__main__":
    unittest.main()
