"""Tests for the multiagent-orchestration skill (PRO-28)."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from prompticorn.builders.errors import BuilderException
from prompticorn.ir.loaders.skill_loader import SkillLoader
from prompticorn.ir.models import Agent
from prompticorn.prompt_builder import PromptBuilder

_SKILL = "multiagent-orchestration"
_VARIANTS = ["minimal", "verbose"]


def _skill_path(skills_dir: Path, variant: str) -> Path:
    return skills_dir / _SKILL / variant / "SKILL.md"


class TestMultiagentOrchestrationSkill:
    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_skill_file_exists(self, skills_dir, variant):
        assert _skill_path(skills_dir, variant).exists()

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_discovered_by_loader(self, skills_dir, variant):
        skill = SkillLoader().load(str(_skill_path(skills_dir, variant)))
        assert skill.name == _SKILL
        assert skill.description

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_covers_the_six_procedure_steps(self, skills_dir, variant):
        body = _skill_path(skills_dir, variant).read_text().lower()
        for phrase in [
            "load conventions",
            "discover agents",
            "execution model",
            "environment-readiness",  # the hard env gate
            "approval",  # the plan-before-work gate
            "concurrent",  # concurrent execution
        ]:
            assert phrase in body, f"{variant}: missing '{phrase}'"

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_references_but_does_not_duplicate_workflows(self, skills_dir, variant):
        body = _skill_path(skills_dir, variant).read_text()
        assert "multi-agent-coordination" in body
        assert "workflow-orchestration-patterns" in body
        # It is a prompt/config generator concern, not a runtime — make that explicit.
        assert "not a" in body.lower() and "runtime" in body.lower()

    def test_wired_to_orchestrator(self, project_root):
        mapping = yaml.safe_load(
            (project_root / "prompticorn" / "configurations" / "agent_skill_mapping.yaml").read_text()
        )
        assert _SKILL in mapping["orchestrator"]["skills"]

    @pytest.mark.parametrize(
        ("tool", "expected"),
        [
            ("claude", ".claude/skills/multiagent-orchestration/SKILL.md"),
            ("copilot", ".github/skills/multiagent-orchestration.md"),
        ],
    )
    def test_emitted_to_each_assistant_primitive(self, tool, expected):
        """An agent carrying the skill emits it to each builder's nearest primitive
        (folder SKILL.md for claude; flat file for copilot)."""
        agent = Agent(
            name="orchestrator",
            description="Coordinate multi-step workflows",
            system_prompt="You coordinate.",
            skills=[_SKILL],
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            try:
                written = PromptBuilder(tool)._write_skill_files(root, "orchestrator", agent, "minimal")
            except BuilderException as exc:  # pragma: no cover - defensive
                pytest.fail(f"{tool} failed to emit the skill: {exc}")
            assert expected in written
            assert (root / expected).exists()
