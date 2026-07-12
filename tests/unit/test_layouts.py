"""Unit tests for per-tool write-layout strategies (PRO-60 / F2b)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prompticorn.builders.layouts import (
    ClaudeLayout,
    ClineLayout,
    CopilotLayout,
    CursorLayout,
    KiloLayout,
    get_layout,
)


class TestLayoutResolution(unittest.TestCase):
    def test_get_layout_by_builder_name(self) -> None:
        self.assertIsInstance(get_layout("kilo"), KiloLayout)
        self.assertIsInstance(get_layout("cline"), ClineLayout)
        self.assertIsInstance(get_layout("cursor"), CursorLayout)
        self.assertIsInstance(get_layout("copilot"), CopilotLayout)
        self.assertIsInstance(get_layout("claude"), ClaudeLayout)

    def test_unknown_layout_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_layout("nope")


class TestLayoutCapabilities(unittest.TestCase):
    def test_only_kilo_writes_subagents_workflows_rules(self) -> None:
        kilo = get_layout("kilo")
        self.assertTrue(kilo.writes_subagents)
        self.assertTrue(kilo.writes_workflows)
        self.assertTrue(kilo.writes_rules)
        for other in ("cline", "cursor", "copilot", "claude"):
            layout = get_layout(other)
            self.assertFalse(layout.writes_subagents)
            self.assertFalse(layout.writes_workflows)
            self.assertFalse(layout.writes_rules)

    def test_only_claude_emits_claude_md(self) -> None:
        self.assertTrue(get_layout("claude").emits_claude_md)
        self.assertEqual(get_layout("claude").root_doc_filename(), "CLAUDE.md")
        for other in ("kilo", "cline", "cursor", "copilot"):
            self.assertFalse(get_layout(other).emits_claude_md)
            self.assertEqual(get_layout(other).root_doc_filename(), "AGENTS.md")


class TestLayoutWrites(unittest.TestCase):
    def test_kilo_agent_per_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = get_layout("kilo").write_agent(root, "code", "body")
            self.assertEqual(written, [".kilo/agents/code.md"])
            self.assertEqual((root / ".kilo/agents/code.md").read_text(), "body")

    def test_concat_layout_appends(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = get_layout("cline")
            layout.write_agent(root, "a", "first")
            layout.write_agent(root, "b", "second")
            self.assertEqual((root / ".clinerules").read_text(), "first\n\nsecond")

    def test_claude_dict_output_writes_each_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = get_layout("claude").write_agent(
                root, "code", {".claude/agents/code.md": "x", "CLAUDE.local": "y"}
            )
            self.assertEqual(set(written), {".claude/agents/code.md", "CLAUDE.local"})
            self.assertEqual((root / ".claude/agents/code.md").read_text(), "x")

    def test_skill_folder_vs_flat(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                get_layout("claude").write_skill(root, "verify", "c"),
                [".claude/skills/verify/SKILL.md"],
            )
            self.assertEqual(
                get_layout("copilot").write_skill(root, "verify", "c"),
                [".github/skills/verify.md"],
            )


if __name__ == "__main__":
    unittest.main()
