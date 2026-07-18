"""Unit tests for the OpenAI Codex generator (PRO-16)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

if sys.version_info >= (3, 11):
    import tomllib
else:  # Python 3.10 has no stdlib tomllib
    import tomli as tomllib

import yaml

from prompticorn.artifacts import ArtifactManager
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.codex_builder import CodexBuilder, generate_codex_config
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent
from prompticorn.prompt_builder import get_prompt_builder

_OPTS = BuildOptions(variant="minimal")
_CFG = {
    "variant": "minimal",
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
}


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


class TestCodexBuilder(unittest.TestCase):
    def test_agent_as_skill_frontmatter(self) -> None:
        text = CodexBuilder().build(_agent("architect", "Designs systems"), _OPTS)
        fm = yaml.safe_load(text.split("---\n")[1])
        self.assertRegex(fm["name"], r"^[a-z0-9-]+$")
        self.assertEqual(fm["description"], "Designs systems")

    def test_config_toml_parses(self) -> None:
        parsed = tomllib.loads(generate_codex_config())
        self.assertEqual(parsed["approval_policy"], "on-request")
        self.assertEqual(parsed["sandbox_mode"], "workspace-write")


class TestCodexLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("codex")

    def test_capabilities(self) -> None:
        self.assertFalse(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_claude_md)
        # Codex reads AGENTS.md, so the root doc is emitted.
        self.assertTrue(self.layout.emits_agents_md)

    def test_agent_and_skill_to_agents_skills(self) -> None:
        content = CodexBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content), [".agents/skills/code/SKILL.md"]
            )
            self.assertEqual(
                self.layout.write_skill(root, "verify", "c"), [".agents/skills/verify/SKILL.md"]
            )

    def test_finalize_writes_codex_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.finalize(root, [], None), [".codex/config.toml"])
            self.assertTrue((root / ".codex/config.toml").exists())


class TestCodexZedDetection(unittest.TestCase):
    """The core collision fix: current_tool must tell Codex from Zed."""

    def test_codex_project_detected_as_codex(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("codex").build(root, _CFG, dry_run=False)
            # Codex writes both .agents/ (shared with Zed) and .codex/ (unique).
            self.assertTrue((root / ".agents").exists())
            self.assertTrue((root / ".codex" / "config.toml").exists())
            self.assertEqual(ArtifactManager(root).current_tool, "codex")

    def test_zed_project_detected_as_zed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("zed").build(root, _CFG, dry_run=False)
            self.assertFalse((root / ".codex").exists())
            self.assertEqual(ArtifactManager(root).current_tool, "zed")


if __name__ == "__main__":
    unittest.main()
