"""Tests for the multiagent-orchestration skill (PRO-28)."""

import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from prompticorn.builders.errors import BuilderException
from prompticorn.ir.loaders.skill_loader import SkillLoader
from prompticorn.ir.models import Agent
from prompticorn.prompt_builder import PromptBuilder, get_prompt_builder

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
        # The loader parses text; fetching bytes is the caller's job. (PRO-105)
        path = _skill_path(skills_dir, variant)
        skill = SkillLoader().parse(path.read_text(encoding="utf-8"), source=str(path))
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
            (
                project_root / "prompticorn" / "configurations" / "agent_skill_mapping.yaml"
            ).read_text()
        )
        assert _SKILL in mapping["orchestrator"]["skills"]

    @pytest.mark.parametrize(
        ("tool", "expected"),
        [
            ("claude", ".claude/skills/multiagent-orchestration/SKILL.md"),
            ("copilot", ".github/skills/multiagent-orchestration/SKILL.md"),
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
                written = PromptBuilder(tool)._write_skill_files(
                    root, "orchestrator", agent, "minimal"
                )
            except BuilderException as exc:  # pragma: no cover - defensive
                pytest.fail(f"{tool} failed to emit the skill: {exc}")
            assert expected in written
            assert (root / expected).exists()

    def test_reaches_single_language_build(self):
        """PRO-62: agent-level skills (from the mapping) must survive a
        single-language build. Previously a language override replaced the
        agent-level skill set, dropping the orchestrator's skills entirely."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("claude").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            # The agent-level skill reaches the build even though python has a
            # language override that does not list it.
            assert (root / ".claude" / "skills" / _SKILL / "SKILL.md").exists()

    def test_orchestrator_prompt_can_invoke_the_skill(self, project_root):
        """PRO-91: the mapping alone only *lists* the skill in a table. The
        orchestrator's own prompt must tell it to reach for the procedure,
        otherwise its flow stays sequential and the skill is never invoked."""
        prompt = (
            project_root / "prompticorn" / "agents" / "orchestrator" / "prompt.md"
        ).read_text()
        assert _SKILL in prompt
        body = prompt.lower()
        # It must convey the trigger (parallelism) and that the gates are hard.
        assert "parallel" in body
        assert "gate" in body

    def test_orchestrator_build_output_references_the_skill(self):
        """The skill reaches the orchestrator's generated markdown, not just the
        source prompt."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("claude").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            orchestrator = (root / ".claude" / "agents" / "orchestrator-agent.md").read_text()
            assert f".claude/skills/{_SKILL}/SKILL.md" in orchestrator

    def test_no_dangling_skill_references_in_single_language_build(self):
        """Every skill a built agent's markdown references must have its SKILL.md
        emitted on disk (no broken links)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("claude").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            referenced = set()
            for md in (root / ".claude" / "agents").glob("*.md"):
                referenced.update(re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", md.read_text()))
            missing = sorted(
                name
                for name in referenced
                if not (root / ".claude" / "skills" / name / "SKILL.md").exists()
            )
            assert not missing, f"dangling skill references: {missing}"
