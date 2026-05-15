"""Test that each tool ONLY creates its own artifacts, not other tools' artifacts."""

import shutil
import unittest
from pathlib import Path

from prompticorn.prompt_builder import get_prompt_builder


class TestToolArtifactIsolation(unittest.TestCase):
    """Verify complete artifact isolation - each tool only creates its own files."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_tool_isolation")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def _get_all_artifacts(self):
        """Get all tool artifact directories."""
        return {
            "kilo": self.test_dir / ".kilo",
            "claude": self.test_dir / ".claude",
            "cline": self.test_dir / ".cline",
            "cursor": self.test_dir / ".cursor",
            "copilot": self.test_dir / ".github",
            "custom_instructions": self.test_dir / "custom_instructions",
            "opencode": self.test_dir / ".opencode",
            "rules": self.test_dir / "rules",  # Should NEVER exist
        }

    def _build_for_tool(self, tool_name):
        """Build for a specific tool."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        builder = get_prompt_builder(tool_name)
        builder.build(self.test_dir, config, dry_run=False)

    def test_kilo_ide_isolation(self):
        """Test Kilo IDE only creates .kilo/ artifacts."""
        self._build_for_tool("kilo-ide")
        artifacts = self._get_all_artifacts()

        # Should exist
        self.assertTrue(artifacts["kilo"].exists(), ".kilo/ should exist for Kilo")

        # Should NOT exist
        self.assertFalse(artifacts["claude"].exists(), ".claude/ should NOT exist")
        self.assertFalse(artifacts["cline"].exists(), ".cline/ should NOT exist")
        self.assertFalse(artifacts["cursor"].exists(), ".cursor/ should NOT exist")
        self.assertFalse(artifacts["copilot"].exists(), ".github/ should NOT exist")
        self.assertFalse(
            artifacts["custom_instructions"].exists(), "custom_instructions/ should NOT exist"
        )
        self.assertFalse(artifacts["rules"].exists(), "rules/ should NEVER exist at root")

    def test_claude_isolation(self):
        """Test Claude only creates .claude/ and CLAUDE.md artifacts."""
        self._build_for_tool("claude")
        artifacts = self._get_all_artifacts()

        # Should exist
        self.assertTrue(artifacts["claude"].exists(), ".claude/ should exist for Claude")
        self.assertTrue(
            (self.test_dir / "CLAUDE.md").exists(),
            "CLAUDE.md should exist for Claude",
        )

        # Should NOT exist
        self.assertFalse(artifacts["kilo"].exists(), ".kilo/ should NOT exist")
        self.assertFalse(artifacts["cline"].exists(), ".cline/ should NOT exist")
        self.assertFalse(artifacts["cursor"].exists(), ".cursor/ should NOT exist")
        self.assertFalse(artifacts["copilot"].exists(), ".github/ should NOT exist (for this test)")
        self.assertFalse(
            artifacts["custom_instructions"].exists(),
            "custom_instructions/ should NOT exist for Claude",
        )
        self.assertFalse(artifacts["rules"].exists(), "rules/ should NEVER exist at root")

    def test_cline_isolation(self):
        """Test Cline only creates .cline/ artifacts."""
        self._build_for_tool("cline")
        artifacts = self._get_all_artifacts()

        # Should exist
        self.assertTrue(artifacts["cline"].exists(), ".cline/ should exist for Cline")

        # Should NOT exist
        self.assertFalse(artifacts["kilo"].exists(), ".kilo/ should NOT exist")
        self.assertFalse(artifacts["claude"].exists(), ".claude/ should NOT exist")
        self.assertFalse(artifacts["cursor"].exists(), ".cursor/ should NOT exist")
        self.assertFalse(
            artifacts["custom_instructions"].exists(), "custom_instructions/ should NOT exist"
        )
        self.assertFalse(artifacts["rules"].exists(), "rules/ should NEVER exist at root")

    def test_cursor_isolation(self):
        """Test Cursor only creates .cursor/ artifacts."""
        self._build_for_tool("cursor")
        artifacts = self._get_all_artifacts()

        # Should exist
        self.assertTrue(artifacts["cursor"].exists(), ".cursor/ should exist for Cursor")

        # Should NOT exist
        self.assertFalse(artifacts["kilo"].exists(), ".kilo/ should NOT exist")
        self.assertFalse(artifacts["claude"].exists(), ".claude/ should NOT exist")
        self.assertFalse(artifacts["cline"].exists(), ".cline/ should NOT exist")
        self.assertFalse(
            artifacts["custom_instructions"].exists(), "custom_instructions/ should NOT exist"
        )
        self.assertFalse(artifacts["rules"].exists(), "rules/ should NEVER exist at root")

    def test_no_mixed_artifacts(self):
        """Test that no two tools create overlapping artifacts."""
        # Build with Claude
        self._build_for_tool("claude")
        claude_artifacts = list(self.test_dir.glob("*")) + list(self.test_dir.glob(".*"))

        # Clean and build with Cline
        shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

        self._build_for_tool("cline")
        cline_artifacts = list(self.test_dir.glob("*")) + list(self.test_dir.glob(".*"))

        # Check for overlaps
        claude_names = {p.name for p in claude_artifacts}
        cline_names = {p.name for p in cline_artifacts}

        # These should NOT overlap (tool-specific artifacts)
        problematic_overlaps = {".kilo", ".claude", "CLAUDE.md", "custom_instructions"} & (
            claude_names & cline_names
        )
        self.assertEqual(
            problematic_overlaps,
            set(),
            f"Tool-specific artifacts should NOT overlap: {problematic_overlaps}",
        )


if __name__ == "__main__":
    unittest.main()
