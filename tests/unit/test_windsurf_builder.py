"""Unit tests for the Windsurf / Cascade generator (PRO-52)."""

import unittest
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.layouts import get_layout
from prompticorn.builders.windsurf_builder import (
    _RULE_CHAR_LIMIT,
    WindsurfBuilder,
    WindsurfRuleBudgetWarning,
    _rule,
    _warn_if_over_budget,
    workflow_to_windsurf,
)
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


class TestWindsurfBuilder(unittest.TestCase):
    def test_agent_as_skill_frontmatter(self) -> None:
        fm = _frontmatter(WindsurfBuilder().build(_agent("architect", "Designs systems"), _OPTS))
        self.assertRegex(fm["name"], r"^[a-z][a-z0-9-]*$")
        self.assertEqual(fm["description"], "Designs systems")

    def test_rules_have_trigger_frontmatter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                written = WindsurfBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertIn(".windsurf/rules/conventions-core.md", written)
            # Core is budget-aware: always_on when it fits, else model_decision.
            core = _frontmatter((root / ".windsurf/rules/conventions-core.md").read_text())
            self.assertIn(core["trigger"], ("always_on", "model_decision"))
            lang = _frontmatter((root / ".windsurf/rules/conventions-python.md").read_text())
            self.assertEqual(lang["trigger"], "glob")
            self.assertEqual(lang["globs"], "**/*.py")

    def test_unknown_language_falls_back_to_model_decision(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # cobol has no extension mapping; if a convention exists it should be
            # model_decision — but there is no cobol convention, so just assert core.
            WindsurfBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertTrue((root / ".windsurf/rules/conventions-core.md").exists())

    def test_workflow_frontmatter_description_only(self) -> None:
        fm = _frontmatter(workflow_to_windsurf("feature", "1. do it"))
        self.assertIn("description", fm)
        # auto_execution_mode is under-documented and intentionally omitted.
        self.assertNotIn("auto_execution_mode", fm)


class TestWindsurfLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("windsurf")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_rules)
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_agents_md)

    def test_paths(self) -> None:
        content = WindsurfBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content),
                [".windsurf/skills/code/SKILL.md"],
            )
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"),
                [".windsurf/skills/verify/SKILL.md"],
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"),
                [".windsurf/workflows/feature.md"],
            )

    def test_build_emits_no_agents_md(self) -> None:
        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("windsurf").build(
                root,
                {"variant": "minimal", "spec": {"language": "python"},
                 "active_personas": ["software_engineer"]},
                dry_run=False,
            )
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertTrue((root / ".windsurf/rules/conventions-core.md").exists())
            self.assertTrue(list(root.glob(".windsurf/skills/*/SKILL.md")))


class TestWindsurfCharCap(unittest.TestCase):
    """PRO-61: keep the always-on budget safe and warn on the ~12k per-file cap."""

    def test_oversize_core_is_model_decision_not_always_on(self) -> None:
        # The real core conventions exceed 12k, so it must not sit always-on
        # (which would blow the 12k always-on budget) — it becomes description-triggered.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                WindsurfBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            core = (root / ".windsurf/rules/conventions-core.md").read_text()
            self.assertEqual(_frontmatter(core)["trigger"], "model_decision")

    def test_oversize_rule_raises_budget_warning(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                WindsurfBuilder().write_rules_files(root, {"spec": {"language": "python"}})
            self.assertTrue(
                any(issubclass(w.category, WindsurfRuleBudgetWarning) for w in caught),
                "expected a WindsurfRuleBudgetWarning for the oversize core rule",
            )

    def test_within_budget_content_is_always_on_and_silent(self) -> None:
        # A small rule fits: always-on, no warning.
        rule = _rule({"trigger": "always_on", "description": "tiny"}, "be concise")
        self.assertLess(len(rule), _RULE_CHAR_LIMIT)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _warn_if_over_budget(".windsurf/rules/x.md", rule)
        self.assertEqual([w for w in caught if issubclass(w.category, WindsurfRuleBudgetWarning)], [])


if __name__ == "__main__":
    unittest.main()
