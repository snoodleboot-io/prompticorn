"""Unit tests for the Junie CLI generator (PRO-38)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.junie_builder import JunieBuilder, slugify
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", tools=None, skills=None):
    return Agent(
        name=name,
        description=f"{name} agent purpose",
        system_prompt=f"You are {name}.",
        tools=tools or [],
        skills=skills or [],
    )


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


class TestSlugify(unittest.TestCase):
    def test_slug_starts_with_letter(self) -> None:
        for raw in ["code", "3d-render", "ML/AI", "  weird  ", "123"]:
            slug = slugify(raw)
            self.assertRegex(slug, r"^[a-z][a-z0-9-]*$")


class TestJunieBuilderBuild(unittest.TestCase):
    def test_frontmatter_and_body(self) -> None:
        text = JunieBuilder().build(_agent("architect"), _OPTS)
        self.assertTrue(text.startswith("---\n"))
        fm = _frontmatter(text)
        self.assertRegex(fm["name"], r"^[a-z][a-z0-9-]*$")
        self.assertTrue(fm["description"])
        self.assertIn("You are architect.", text)

    def test_tools_mapped_to_junie_groups(self) -> None:
        fm = _frontmatter(JunieBuilder().build(_agent(tools=["read", "write", "bash"]), _OPTS))
        self.assertLessEqual(
            set(fm["tools"]),
            {"Read", "Bash", "Glob", "Grep", "Write", "Edit", "WebSearch", "AskUserQuestion"},
        )
        self.assertIn("Write", fm["tools"])
        self.assertIn("Bash", fm["tools"])

    def test_readonly_agent_has_no_write(self) -> None:
        fm = _frontmatter(JunieBuilder().build(_agent("ask", tools=["read"]), _OPTS))
        self.assertNotIn("Write", fm["tools"])
        self.assertNotIn("Bash", fm["tools"])

    def test_skills_included_when_requested(self) -> None:
        fm = _frontmatter(JunieBuilder().build(_agent(skills=["verify"]), _OPTS))
        self.assertEqual(fm["skills"], ["verify"])


class TestJunieLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("junie")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.writes_subagents)
        self.assertFalse(self.layout.emits_claude_md)
        self.assertEqual(self.layout.root_doc_filename(), "AGENTS.md")

    def test_write_agent_one_file_each(self) -> None:
        content = JunieBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = self.layout.write_agent(root, "code", content)
            self.assertEqual(written, [".junie/agents/code.md"])
            self.assertTrue((root / ".junie/agents/code.md").exists())

    def test_skill_and_workflow_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"), [".junie/skills/verify/SKILL.md"]
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"), [".junie/commands/feature.md"]
            )

    def test_no_aggregate_finalize(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.finalize(root, ["x"], None), [])


if __name__ == "__main__":
    unittest.main()
