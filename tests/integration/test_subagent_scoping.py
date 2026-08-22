"""Test that subagents are only written for Kilo tool."""

import tempfile
import unittest
from pathlib import Path

from prompticorn.prompt_builder import get_prompt_builder


class TestSubagentScoping(unittest.TestCase):
    """Verify subagents are ONLY created for Kilo, not for Claude/Cline/Cursor/Copilot."""

    def setUp(self):
        """Set up test fixtures.

        The directory is a real temp directory, not a CWD-relative one. A test
        that writes into the working tree leaves debris behind whenever the run
        does not reach teardown — a crash, a Ctrl-C, a ``-x`` bail-out — and
        that debris is generated output sitting next to real source. Registering
        the cleanup with ``addCleanup`` rather than a ``tearDown`` means it also
        runs when ``setUp`` itself fails partway. (PRO-147)
        """
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.test_dir = Path(tmp.name)

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
