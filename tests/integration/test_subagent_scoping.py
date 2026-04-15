"""Test that subagents are only written for Kilo tool."""

import shutil
import unittest
from pathlib import Path

from promptosaurus.prompt_builder import get_prompt_builder


class TestSubagentScoping(unittest.TestCase):
    """Verify subagents are ONLY created for Kilo, not for Claude/Cline/Cursor/Copilot."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_subagent_scoping")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_claude_does_not_create_subagents(self):
        """Test that Claude builder does NOT create .kilo/agents/ subagents."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        builder = get_prompt_builder("claude")
        builder.build(self.test_dir, config, dry_run=False)

        # BUG CHECK: .kilo/agents should NOT exist
        kilo_agents = self.test_dir / ".kilo" / "agents"
        self.assertFalse(
            kilo_agents.exists(),
            "BUG FIXED: .kilo/agents/ should NOT be created when tool_name is 'claude'",
        )

    def test_kilo_ide_creates_subagents(self):
        """Test that Kilo IDE builder DOES create .kilo/agents/ subagents."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        builder = get_prompt_builder("kilo-ide")
        builder.build(self.test_dir, config, dry_run=False)

        # Verify: .kilo/agents MUST exist
        kilo_agents = self.test_dir / ".kilo" / "agents"
        self.assertTrue(
            kilo_agents.exists(), ".kilo/agents/ MUST be created when tool_name is 'kilo'"
        )

        # Verify: Has subagent files
        subagent_files = list(kilo_agents.glob("*/*.md"))
        self.assertGreater(
            len(subagent_files),
            0,
            "Kilo should create subagent files in .kilo/agents/{agent}/{subagent}.md",
        )


if __name__ == "__main__":
    unittest.main()
