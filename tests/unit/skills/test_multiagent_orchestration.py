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
from prompticorn.text_utils import frontmatter_field, parse_frontmatter

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

    @pytest.mark.parametrize("agent", ["plan", "architect", "code"])
    def test_wired_to_the_agents_that_plan_work(self, project_root, agent):
        """PRO-142: mapped to the orchestrator alone, the skill was invisible during
        planning — planning routes to plan-agent, which never saw it. The agents that
        decide how work is decomposed must carry it too."""
        mapping = yaml.safe_load(
            (
                project_root / "prompticorn" / "configurations" / "agent_skill_mapping.yaml"
            ).read_text()
        )
        assert _SKILL in mapping[agent]["skills"]

    def test_every_mapping_key_names_a_real_agent(self, project_root):
        """PRO-142: `planning:` addressed no agent, so plan-agent silently fell back
        to defaults. A key that matches nothing is dead config that looks live."""
        root = project_root / "prompticorn"
        mapping = yaml.safe_load((root / "configurations" / "agent_skill_mapping.yaml").read_text())
        agents = {p.name for p in (root / "agents").iterdir() if (p / "prompt.md").exists()}
        assert not sorted(set(mapping) - agents)

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_declares_a_trigger_for_loading(self, skills_dir, variant):
        """The emitted skill table shows `when_to_use`; without it the row falls back
        to "When workflow requires <name>", which states no condition at all."""
        path = _skill_path(skills_dir, variant)
        trigger = frontmatter_field(path.read_text(encoding="utf-8"), "when_to_use")
        assert trigger and "parallel" in trigger.lower()

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_covers_the_gaps_the_procedure_depends_on(self, skills_dir, variant):
        """PRO-142: the spec's hard requirements that the skill body had dropped."""
        body = _skill_path(skills_dir, variant).read_text().lower()
        for phrase, why in [
            ("environment-setup", "names the subagent that owns the env gate"),
            ("interfaces", "each subagent brief declares its shared interfaces"),
            ("own subagents", "units with parallelisable subtasks spawn recursively"),
            ("markdown", "the plan is delivered as a markdown document"),
            ("re-present", "material mid-run change pauses lanes and re-presents"),
        ]:
            assert phrase in body, f"{variant}: missing '{phrase}' — {why}"

    def test_environment_setup_subagent_exists(self, project_root):
        """Step 4 gates on a dedicated setup subagent; it must be a real agent with
        the tooling to actually start a service, not a doc that describes one."""
        subagent = (
            project_root
            / "prompticorn"
            / "agents"
            / "orchestrator"
            / "subagents"
            / "environment-setup"
        )
        for variant in _VARIANTS:
            text = (subagent / variant / "prompt.md").read_text(encoding="utf-8")
            metadata, _ = parse_frontmatter(text)
            assert "bash" in metadata["tools"], f"{variant}: cannot start anything without bash"
            assert frontmatter_field(text, "when_to_use")

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
