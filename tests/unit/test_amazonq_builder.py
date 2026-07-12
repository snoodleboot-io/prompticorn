"""Unit tests for the Amazon Q Developer CLI generator (PRO-49)."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prompticorn.builders.amazonq_builder import AmazonQBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


class TestAmazonQBuilder(unittest.TestCase):
    def test_agent_json_shape(self) -> None:
        d = json.loads(AmazonQBuilder().build(_agent("architect", "Designs systems"), _OPTS))
        self.assertRegex(d["name"], r"^[a-z][a-z0-9-]*$")
        self.assertEqual(d["description"], "Designs systems")
        self.assertEqual(d["prompt"], "You are code.")
        self.assertEqual(d["tools"], ["*"])

    def test_agent_resources_include_rules_glob(self) -> None:
        # Custom agents do not inherit default resources, so the rules glob must
        # be present or conventions never load.
        d = json.loads(AmazonQBuilder().build(_agent(), _OPTS))
        self.assertIn("file://.amazonq/rules/**/*.md", d["resources"])

    def test_write_rules_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = AmazonQBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertIn(".amazonq/rules/conventions.md", written)
            self.assertTrue((root / ".amazonq/rules/conventions.md").exists())


class TestAmazonQLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("amazonq")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_rules)
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_claude_md)
        # Amazon Q does not read AGENTS.md — the root doc must be suppressed.
        self.assertFalse(self.layout.emits_agents_md)

    def test_agent_json_and_prompt_paths(self) -> None:
        content = AmazonQBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content),
                [".amazonq/cli-agents/code.json"],
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"),
                [".amazonq/prompts/feature.md"],
            )

    def test_skill_dropped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.write_skill(root, "verify", "c"), [])
            self.assertFalse((root / ".amazonq").exists())


class TestAmazonQNoAgentsMd(unittest.TestCase):
    def test_build_emits_no_root_agents_md(self) -> None:
        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("amazonq").build(
                root,
                {"variant": "minimal", "spec": {"language": "python"},
                 "active_personas": ["software_engineer"]},
                dry_run=False,
            )
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertFalse((root / "CLAUDE.md").exists())
            self.assertTrue((root / ".amazonq/rules/conventions.md").exists())
            self.assertTrue(list(root.glob(".amazonq/cli-agents/*.json")))


if __name__ == "__main__":
    unittest.main()
