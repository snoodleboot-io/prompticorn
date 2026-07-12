"""Unit tests for the Roo Code generator (PRO-34)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.layouts import get_layout
from prompticorn.builders.roo_builder import RooBuilder, generate_roomodes, slugify
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", tools=None, skills=None, workflows=None):
    return Agent(
        name=name,
        description=f"{name} agent purpose",
        system_prompt=f"You are {name}.",
        tools=tools or [],
        skills=skills or [],
        workflows=workflows or [],
    )


class TestSlugify(unittest.TestCase):
    def test_valid_slug_regex(self) -> None:
        for raw in ["code", "Kilo CLI", "a/b/c", "ML & AI", "  weird__name  "]:
            slug = slugify(raw)
            self.assertRegex(slug, r"^[a-zA-Z0-9-]+$")
            self.assertEqual(slug, slug.lower())

    def test_empty_falls_back(self) -> None:
        self.assertEqual(slugify("///"), "mode")


class TestRooBuilderBuild(unittest.TestCase):
    def test_mode_entry_required_fields(self) -> None:
        entry = RooBuilder().build(_agent("architect"), _OPTS)
        for key in ("slug", "name", "roleDefinition", "whenToUse", "groups", "instructions"):
            self.assertIn(key, entry)
        self.assertTrue(entry["roleDefinition"])
        self.assertRegex(entry["slug"], r"^[a-zA-Z0-9-]+$")

    def test_groups_are_valid_subset(self) -> None:
        entry = RooBuilder().build(_agent(tools=["read", "write", "bash"]), _OPTS)
        self.assertLessEqual(set(entry["groups"]), {"read", "edit", "command", "mcp", "modes"})
        self.assertIn("edit", entry["groups"])  # has write
        self.assertIn("command", entry["groups"])  # has bash

    def test_readonly_agent_has_no_edit_group(self) -> None:
        entry = RooBuilder().build(_agent("ask", tools=["read", "search"]), _OPTS)
        self.assertNotIn("edit", entry["groups"])
        self.assertNotIn("command", entry["groups"])

    def test_instructions_carry_prompt_and_skills(self) -> None:
        entry = RooBuilder().build(_agent(skills=["verify"], workflows=["feature"]), _OPTS)
        self.assertIn("You are code.", entry["instructions"])
        self.assertIn("verify", entry["instructions"])
        self.assertIn("feature", entry["instructions"])


class TestGenerateRoomodes(unittest.TestCase):
    def test_sorted_by_slug_and_valid_yaml(self) -> None:
        entries = [RooBuilder().build(_agent(n), _OPTS) for n in ("test", "architect", "code")]
        text = generate_roomodes(entries)
        data = yaml.safe_load(text)
        slugs = [m["slug"] for m in data["customModes"]]
        self.assertEqual(slugs, sorted(slugs))
        for mode in data["customModes"]:
            self.assertTrue(mode["slug"] and mode["name"] and mode["roleDefinition"])
            self.assertIn("groups", mode)


class TestRooLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("roo")

    def test_layout_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.writes_subagents)
        self.assertFalse(self.layout.emits_claude_md)
        self.assertEqual(self.layout.root_doc_filename(), "AGENTS.md")

    def test_write_agent_goes_to_mode_rules(self) -> None:
        entry = RooBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = self.layout.write_agent(root, "code", entry)
            self.assertEqual(written, [".roo/rules-code/01-instructions.md"])
            self.assertTrue((root / ".roo/rules-code/01-instructions.md").exists())

    def test_write_skill_and_workflow_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"), [".roo/skills/verify/SKILL.md"]
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"), [".roo/commands/feature.md"]
            )

    def test_finalize_writes_roomodes(self) -> None:
        entries = [RooBuilder().build(_agent(n), _OPTS) for n in ("code", "test")]
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = self.layout.finalize(root, entries, None)
            self.assertEqual(written, [".roomodes"])
            data = yaml.safe_load((root / ".roomodes").read_text())
            self.assertEqual({m["slug"] for m in data["customModes"]}, {"code", "test"})

    def test_finalize_noop_without_mode_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.finalize(root, ["a string", {"x": 1}], None), [])
            self.assertFalse((root / ".roomodes").exists())


if __name__ == "__main__":
    unittest.main()
