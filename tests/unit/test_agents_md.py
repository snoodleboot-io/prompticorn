"""Unit tests for the canonical AGENTS.md emitter (PRO-31 / E1)."""

import unittest

from prompticorn.builders.agents_md import generate_agents_md

_AGENTS = [
    {"name": "code", "description": "Agent: write and refactor code"},
    {"name": "test", "description": "write comprehensive tests"},
]


class TestAgentsMdEmitter(unittest.TestCase):
    """Verify AGENTS.md is a self-contained baseline: routing index + conventions."""

    def test_starts_with_agents_header(self) -> None:
        self.assertTrue(generate_agents_md(_AGENTS).startswith("# Agents"))

    def test_contains_routing_table_for_each_agent(self) -> None:
        out = generate_agents_md(_AGENTS)
        self.assertIn("| Agent | Purpose |", out)
        self.assertIn("| **code** |", out)
        self.assertIn("| **test** |", out)

    def test_cleans_agent_prefix_and_capitalizes(self) -> None:
        out = generate_agents_md(_AGENTS)
        self.assertIn("| **code** | Write and refactor code |", out)
        self.assertIn("| **test** | Write comprehensive tests |", out)

    def test_inlines_core_conventions(self) -> None:
        out = generate_agents_md(_AGENTS, primary_language="python")
        # Core conventions section is inlined (not referenced by path).
        self.assertIn("Conventions", out)

    def test_does_not_leak_tool_specific_layout(self) -> None:
        """A generic baseline must not reference any single tool's private dirs."""
        out = generate_agents_md(_AGENTS, primary_language="python")
        self.assertNotIn(".kilo/rules/", out)
        self.assertNotIn(".kilo/agents/", out)

    def test_no_agents_emits_generic_routing_note(self) -> None:
        out = generate_agents_md([])
        self.assertTrue(out.startswith("# Agents"))
        self.assertIn("## Available agents", out)
        self.assertNotIn("| Agent | Purpose |", out)

    def test_ends_with_single_trailing_newline(self) -> None:
        out = generate_agents_md(_AGENTS)
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
