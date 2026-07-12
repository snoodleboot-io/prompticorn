"""Unit tests for the Zed generator (PRO-41)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.layouts import get_layout
from prompticorn.builders.zed_builder import ZedBuilder
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


class TestZedBuilder(unittest.TestCase):
    def test_agent_as_skill_frontmatter(self) -> None:
        text = ZedBuilder().build(_agent("architect", "Designs systems"), _OPTS)
        self.assertTrue(text.startswith("---\n"))
        fm = _frontmatter(text)
        self.assertRegex(fm["name"], r"^[a-z0-9-]+$")
        self.assertEqual(fm["description"], "Designs systems")
        self.assertIn("You are code.", text)

    def test_description_yaml_safe_with_colon(self) -> None:
        # A description with a colon must not break the frontmatter YAML.
        text = ZedBuilder().build(_agent(description="Note: does X and Y"), _OPTS)
        self.assertEqual(_frontmatter(text)["description"], "Note: does X and Y")

    def test_description_is_collapsed_and_capped(self) -> None:
        text = ZedBuilder().build(_agent(description="a  b\n\nc " + "x" * 600), _OPTS)
        desc = _frontmatter(text)["description"]
        self.assertLessEqual(len(desc.encode()), 1024)
        self.assertNotIn("\n", desc)


class TestZedLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("zed")

    def test_capabilities(self) -> None:
        self.assertFalse(self.layout.writes_workflows)
        self.assertFalse(self.layout.writes_subagents)
        self.assertFalse(self.layout.emits_claude_md)
        self.assertEqual(self.layout.root_doc_filename(), "AGENTS.md")

    def test_agent_and_skill_both_go_to_agents_skills(self) -> None:
        content = ZedBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content),
                [".agents/skills/code/SKILL.md"],
            )
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"),
                [".agents/skills/verify/SKILL.md"],
            )
            self.assertTrue((root / ".agents/skills/code/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
