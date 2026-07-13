"""Unit tests for the Aider generator (PRO-58)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.aider_builder import AiderBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


class TestAiderBuilder(unittest.TestCase):
    def test_write_rules_emits_conventions_and_conf(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = AiderBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertEqual(set(written), {"CONVENTIONS.md", ".aider.conf.yml"})
            self.assertTrue((root / "CONVENTIONS.md").exists())
            conf = yaml.safe_load((root / ".aider.conf.yml").read_text())
            # The read: list is what makes aider load CONVENTIONS.md (not auto-discovered).
            self.assertEqual(conf, {"read": ["CONVENTIONS.md"]})

    def test_conventions_include_core(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            AiderBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertIn("Conventions", (root / "CONVENTIONS.md").read_text())


class TestAiderLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("aider")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_rules)
        self.assertFalse(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_agents_md)

    def test_agent_and_skill_are_noops(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.write_agent(root, "code", "x"), [])
            self.assertEqual(self.layout.write_skill(root, "verify", "x"), [])

    def test_build_emits_only_conventions_and_conf(self) -> None:
        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("aider").build(
                root,
                {"variant": "minimal", "spec": {"language": "python"},
                 "active_personas": ["software_engineer"]},
                dry_run=False,
            )
            files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
            self.assertEqual(files, [".aider.conf.yml", "CONVENTIONS.md"])


class TestAgentBuildDiscarded(unittest.TestCase):
    def test_build_returns_empty(self) -> None:
        agent = Agent(name="code", description="d", system_prompt="p")
        self.assertEqual(AiderBuilder().build(agent, _OPTS), "")


if __name__ == "__main__":
    unittest.main()
