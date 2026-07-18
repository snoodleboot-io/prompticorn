"""Integration tests for artifact cleanup during tool switching."""

import shutil
import unittest
from pathlib import Path

from prompticorn.artifacts import ARTIFACT_FILES, ArtifactManager


class TestArtifactCleanup(unittest.TestCase):
    """Test artifact cleanup when switching between tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_artifacts")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
        self.manager = ArtifactManager(self.test_dir)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_kilo_ide_creates_kilo_directory(self):
        """Test that kilo-ide creates .kilo/ directory."""
        artifacts = ARTIFACT_FILES["kilo-ide"]["create"]
        self.assertIn(".kilo/", artifacts)

    def test_claude_creates_claude_directory(self):
        """Test that claude creates .claude/ directory and CLAUDE.md file."""
        artifacts = ARTIFACT_FILES["claude"]["create"]
        self.assertIn(".claude/", artifacts)
        self.assertIn("CLAUDE.md", artifacts)

    def test_remove_artifacts_created_by_kilo(self):
        """Test removing artifacts created by kilo-ide."""
        # Create a fake .kilo/ directory
        kilo_dir = self.test_dir / ".kilo"
        kilo_dir.mkdir()
        (kilo_dir / "test.md").write_text("test")

        self.assertTrue(kilo_dir.exists())

        # Remove artifacts created by kilo-ide
        actions = self.manager.remove_artifacts_created_by("kilo-ide")

        # Verify .kilo/ is removed
        self.assertFalse(kilo_dir.exists())
        self.assertTrue(any("Removed directory: .kilo/" in action for action in actions))

    def test_remove_artifacts_created_by_claude(self):
        """Test removing artifacts created by claude."""
        # Create fake claude artifacts
        claude_dir = self.test_dir / ".claude"
        claude_md = self.test_dir / "CLAUDE.md"
        claude_dir.mkdir()
        (claude_dir / "test.md").write_text("test")
        claude_md.write_text("# Claude routing file")

        self.assertTrue(claude_dir.exists())
        self.assertTrue(claude_md.exists())

        # Remove artifacts created by claude
        actions = self.manager.remove_artifacts_created_by("claude")

        # Verify both .claude/ directory and CLAUDE.md are removed
        self.assertFalse(claude_dir.exists())
        self.assertFalse(claude_md.exists())
        self.assertEqual(len(actions), 2)

    def test_detect_current_tool_kilo_ide(self):
        """Test detecting kilo-ide as current tool."""
        # Create .kilo/ directory
        kilo_dir = self.test_dir / ".kilo"
        kilo_dir.mkdir()

        # Detect tool
        current = self.manager.current_tool
        self.assertEqual(current, "kilo-ide")

    def test_detect_current_tool_claude(self):
        """Test detecting claude as current tool."""
        # Create claude directories
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()

        # Detect tool
        current = self.manager.current_tool
        self.assertEqual(current, "claude")

    def test_switching_from_kilo_to_claude(self):
        """Test switching from kilo-ide to claude.

        Simulates:
        1. Having kilo-ide artifacts
        2. Detecting it as current tool
        3. Removing kilo artifacts
        4. Verifying only claude artifacts exist after removal
        """
        # Setup: only kilo artifacts exist (the real switch flow cleans the old
        # tool BEFORE building the new one, so both are never present at once).
        kilo_dir = self.test_dir / ".kilo"
        kilo_dir.mkdir()
        (kilo_dir / "agents").mkdir()
        (kilo_dir / "agents" / "test.md").write_text("test")

        # Step 1: Detect current tool (should be kilo)
        current_tool = self.manager.current_tool
        self.assertEqual(current_tool, "kilo-ide")

        # Step 2: Remove kilo artifacts
        removal_actions = self.manager.remove_artifacts_created_by(current_tool)

        # Step 3: Verify kilo is removed
        self.assertFalse(kilo_dir.exists())
        self.assertTrue(any("Removed directory: .kilo/" in action for action in removal_actions))

        # Step 4: Now build claude (after the old tool was cleaned).
        claude_dir = self.test_dir / ".claude"
        claude_md = self.test_dir / "CLAUDE.md"
        claude_dir.mkdir()
        (claude_dir / "skills").mkdir()
        claude_md.write_text("# Claude routing file")

        # Step 5: Verify current tool is now detected as claude
        self.assertEqual(self.manager.current_tool, "claude")

    def test_removing_wrong_artifacts_should_fail(self):
        """Test that removing artifacts for non-existent tool returns empty list."""
        actions = self.manager.remove_artifacts_created_by("nonexistent-tool")
        self.assertEqual(actions, [])

    def test_all_tools_have_create_and_remove_artifacts(self):
        """Test that all tools have proper artifact definitions."""
        for tool_name, artifact_config in ARTIFACT_FILES.items():
            self.assertIn("create", artifact_config, f"{tool_name} missing 'create'")
            self.assertIn("remove", artifact_config, f"{tool_name} missing 'remove'")
            self.assertIsInstance(artifact_config["create"], set, f"{tool_name} 'create' not a set")
            self.assertIsInstance(artifact_config["remove"], set, f"{tool_name} 'remove' not a set")

    def test_no_overlap_in_create_artifacts(self):
        """Tools' create artifacts are disjoint except the documented Codex/Zed
        sharing of ``.agents/`` (both emit Agent Skills there; ``current_tool``
        disambiguates via most-specific match — Codex also writes ``.codex/``)."""
        seen = {}
        overlaps = set()
        for tool, config in ARTIFACT_FILES.items():
            for artifact in config["create"]:
                if artifact in seen:
                    overlaps.add((frozenset({seen[artifact], tool}), artifact))
                seen[artifact] = tool

        assert overlaps == {(frozenset({"codex", "zed"}), ".agents/")}, (
            f"unexpected create-artifact overlaps: {overlaps}"
        )


if __name__ == "__main__":
    unittest.main()
