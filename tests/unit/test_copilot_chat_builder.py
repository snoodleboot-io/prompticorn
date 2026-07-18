"""Unit tests for the GitHub Copilot Chat generator (PRO-8)."""

import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.copilot_chat_builder import CopilotChatBuilder, workflow_to_prompt
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent
from prompticorn.prompt_builder import get_prompt_builder

_OPTS = BuildOptions(variant="minimal")


def _agent(name="code", description="Implement features", prompt="You are code."):
    return Agent(name=name, description=description, system_prompt=prompt)


class TestCopilotChatBuilder(unittest.TestCase):
    def test_agent_frontmatter_and_body(self) -> None:
        out = CopilotChatBuilder().build(_agent("architect", "Designs   systems"), _OPTS)
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("name: architect", out)
        # Description whitespace is collapsed.
        self.assertIn("description: Designs systems", out)
        # System prompt is the body after the frontmatter block.
        self.assertIn("\n---\n\nYou are code.", out)

    def test_write_rules_core_and_language_instructions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = CopilotChatBuilder().write_rules_files(
                root, {"spec": {"language": "python"}}
            )
            self.assertIn(".github/instructions/core.instructions.md", written)
            self.assertIn(".github/instructions/conventions-python.instructions.md", written)

            core = (root / ".github/instructions/core.instructions.md").read_text()
            self.assertTrue(core.startswith("---\napplyTo: '**'\n---\n\n"))

            lang = (root / ".github/instructions/conventions-python.instructions.md").read_text()
            # Python conventions are scoped to python files via an applyTo glob.
            self.assertTrue(lang.startswith("---\napplyTo: '**/*.py'\n---\n\n"))

    def test_workflow_to_prompt_single_frontmatter(self) -> None:
        # The workflow's own internal frontmatter must be stripped so the emitted
        # prompt file has exactly one YAML block.
        raw = '---\nname: "feature"\nsubagents: ["code"]\n---\n\n# Feature Workflow\n\nDo it.'
        out = workflow_to_prompt("feature", raw)
        # Exactly one frontmatter block == two "---" delimiter lines.
        self.assertEqual(out.split("\n").count("---"), 2)
        self.assertIn("description: feature workflow", out)
        self.assertIn("# Feature Workflow", out)
        self.assertNotIn('name: "feature"', out)


class TestCopilotChatLayout(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = get_layout("copilot_chat")

    def test_capabilities(self) -> None:
        self.assertTrue(self.layout.writes_rules)
        self.assertTrue(self.layout.writes_workflows)
        self.assertFalse(self.layout.emits_claude_md)
        # Copilot Chat gets native primitives + core.instructions.md, not AGENTS.md.
        self.assertFalse(self.layout.emits_agents_md)

    def test_agent_and_workflow_paths(self) -> None:
        content = CopilotChatBuilder().build(_agent("code"), _OPTS)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                self.layout.write_agent(root, "code", content),
                [".github/agents/code.agent.md"],
            )
            self.assertEqual(
                self.layout.write_workflow(root, "feature", "# body"),
                [".github/prompts/feature.prompt.md"],
            )

    def test_skill_dropped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.layout.write_skill(root, "verify", "c"), [])
            self.assertFalse((root / ".github").exists())


class TestCopilotChatEndToEnd(unittest.TestCase):
    def test_full_build_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("copilot-chat").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            agents = list(root.rglob(".github/agents/*.agent.md"))
            prompts = list(root.rglob(".github/prompts/*.prompt.md"))
            instructions = list(root.rglob(".github/instructions/*.instructions.md"))
            self.assertTrue(agents, "expected custom agent files")
            self.assertTrue(prompts, "expected prompt-file commands")
            self.assertTrue(instructions, "expected applyTo instruction files")
            # No AGENTS.md (native primitives replace it) and no skill files.
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertFalse(list(root.rglob(".github/skills/*")))


if __name__ == "__main__":
    unittest.main()
