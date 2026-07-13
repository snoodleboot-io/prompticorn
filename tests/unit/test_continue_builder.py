"""Unit tests for the Continue.dev generator (PRO-55)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.continue_builder import (
    ContinueBuilder,
    workflow_to_continue_prompt,
)
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


class TestContinueBuilder(unittest.TestCase):
    def test_agent_as_rule_frontmatter(self) -> None:
        fm = _frontmatter(ContinueBuilder().build(_agent("architect", "Designs systems"), _OPTS))
        self.assertEqual(fm["name"], "architect")
        self.assertEqual(fm["description"], "Designs systems")
        # Personas are description-scoped, not always applied.
        self.assertFalse(fm["alwaysApply"])

    def test_convention_rules(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = ContinueBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertIn(".continue/rules/conventions-core.md", written)
            core = _frontmatter((root / ".continue/rules/conventions-core.md").read_text())
            self.assertTrue(core["alwaysApply"])
            lang = _frontmatter((root / ".continue/rules/conventions-python.md").read_text())
            self.assertEqual(lang["globs"], ["**/*.py"])
            self.assertFalse(lang["alwaysApply"])

    def test_prompt_is_invokable(self) -> None:
        fm = _frontmatter(workflow_to_continue_prompt("feature", "1. do it"))
        self.assertTrue(fm["invokable"])
        self.assertEqual(fm["name"], "feature")


class TestContinueLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("continue")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_rules)
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_agents_md)

    def test_paths(self) -> None:
        content = ContinueBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content), [".continue/rules/code.md"]
            )
            self.assertEqual(self.layout.write_skill(root, "verify", "c"), [])
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"),
                [".continue/prompts/feature.md"],
            )

    def test_build_emits_no_agents_md(self) -> None:
        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("continue").build(
                root,
                {"variant": "minimal", "spec": {"language": "python"},
                 "active_personas": ["software_engineer"]},
                dry_run=False,
            )
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertTrue((root / ".continue/rules/conventions-core.md").exists())
            self.assertTrue(list(root.glob(".continue/prompts/*.md")))


if __name__ == "__main__":
    unittest.main()
