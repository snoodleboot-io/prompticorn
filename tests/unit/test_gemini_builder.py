"""Unit tests for the Gemini CLI generator (PRO-45)."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

if sys.version_info >= (3, 11):
    import tomllib
else:  # Python 3.10 has no stdlib tomllib
    import tomli as tomllib

import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.gemini_builder import (
    GeminiBuilder,
    generate_gemini_settings,
    workflow_to_toml,
)
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


class TestGeminiBuilder(unittest.TestCase):
    def test_agent_frontmatter(self) -> None:
        text = GeminiBuilder().build(_agent("architect", "Designs systems"), _OPTS)
        fm = _frontmatter(text)
        self.assertRegex(fm["name"], r"^[a-z][a-z0-9-]*$")
        self.assertEqual(fm["description"], "Designs systems")
        self.assertIn("You are code.", text)

    def test_settings_points_at_agents_md(self) -> None:
        self.assertEqual(
            json.loads(generate_gemini_settings()), {"context": {"fileName": "AGENTS.md"}}
        )

    def test_workflow_toml_parses(self) -> None:
        toml_text = workflow_to_toml("feature", "# Feature\nDo the thing.\n")
        parsed = tomllib.loads(toml_text)
        self.assertIn("prompt", parsed)
        self.assertIn("description", parsed)
        self.assertIn("Do the thing.", parsed["prompt"])

    def test_workflow_toml_literal_string_needs_no_escaping(self) -> None:
        # Backslashes/quotes in the body must survive (literal '''...''' string).
        body = 'path\\to\\file and "quotes" and $var'
        parsed = tomllib.loads(workflow_to_toml("w", body))
        self.assertIn(body, parsed["prompt"])


class TestGeminiLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("gemini")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_claude_md)
        self.assertEqual(self.layout.root_doc_filename(), "AGENTS.md")

    def test_paths(self) -> None:
        content = GeminiBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content), [".gemini/agents/code.md"]
            )
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"), [".gemini/skills/verify/SKILL.md"]
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "c"), [".gemini/commands/feature.toml"]
            )

    def test_finalize_writes_settings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.finalize(root, [], None), [".gemini/settings.json"])
            self.assertEqual(
                json.loads((root / ".gemini/settings.json").read_text()),
                {"context": {"fileName": "AGENTS.md"}},
            )


if __name__ == "__main__":
    unittest.main()
