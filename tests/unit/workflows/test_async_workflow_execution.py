"""Tests for the async-workflow-execution workflow (PRO-91).

The `multiagent-orchestration` skill composes against this workflow for its async
execution model. It was previously an unfilled template mapped to no agent, so the
skill's reference to it dangled in generated output.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from prompticorn.prompt_builder import get_prompt_builder

_WORKFLOW = "async-workflow-execution"
_VARIANTS = ["minimal", "verbose"]

# Markers left behind by the authoring template. Their presence means the file was
# never filled in.
_TEMPLATE_MARKERS = [
    "[First Pattern]",
    "[Second Pattern]",
    "[Third Pattern]",
    "[Details about pattern]",
    "[Code or configuration examples]",
    "[When to use this pattern]",
    "[Pros and cons]",
    "[Practice 1]",
    "[Mistake 1 and how to avoid it]",
    "[Define key concepts and patterns]",
    "[List 4-5 pattern types with brief descriptions]",
    "[When this pattern is applicable]",
    "[Important factors to consider]",
    "[Link to related workflow patterns]",
]


def _workflow_path(workflows_dir: Path, variant: str) -> Path:
    return workflows_dir / _WORKFLOW / variant / "workflow.md"


def _build(root: Path) -> None:
    get_prompt_builder("claude").build(
        root,
        {
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
            "variant": "minimal",
        },
        dry_run=False,
    )


@pytest.mark.unit
class TestAsyncWorkflowExecution:
    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_workflow_file_exists(self, workflows_dir, variant):
        assert _workflow_path(workflows_dir, variant).exists()

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_frontmatter_is_intact(self, workflows_dir, variant):
        text = _workflow_path(workflows_dir, variant).read_text()
        _, frontmatter, _ = text.split("---", 2)
        meta = yaml.safe_load(frontmatter)
        assert meta["name"] == _WORKFLOW
        assert meta["type"] == "workflow"
        assert meta["minimal"] is (variant == "minimal")

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_is_not_an_unfilled_template(self, workflows_dir, variant):
        """The defect PRO-91 fixes: real content, not authoring placeholders."""
        body = _workflow_path(workflows_dir, variant).read_text()
        present = [marker for marker in _TEMPLATE_MARKERS if marker in body]
        assert not present, f"{variant}: unfilled template markers {present}"

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_covers_the_async_execution_model(self, workflows_dir, variant):
        body = _workflow_path(workflows_dir, variant).read_text().lower()
        for phrase in [
            "future",  # future/promise handles
            "callback",  # continuation model
            "fan-out",  # fan-out/fan-in
            "barrier",  # the barrier-vs-pipeline decision
            "pipeline",
            "timeout",  # bounded awaits
        ]:
            assert phrase in body, f"{variant}: missing '{phrase}'"

    @pytest.mark.parametrize("variant", _VARIANTS)
    def test_defers_to_sibling_workflows_rather_than_duplicating(self, workflows_dir, variant):
        """It supplies the execution model only; coordination mechanics stay in
        `multi-agent-coordination`."""
        body = _workflow_path(workflows_dir, variant).read_text()
        assert "multi-agent-coordination" in body
        assert "workflow-orchestration-patterns" in body

    def test_wired_to_orchestrator(self, project_root):
        mapping = yaml.safe_load(
            (
                project_root / "prompticorn" / "configurations" / "agent_skill_mapping.yaml"
            ).read_text()
        )
        assert _WORKFLOW in mapping["orchestrator"]["workflows"]

    def test_emitted_in_single_language_build(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root)
            assert (root / ".claude" / "workflows" / f"{_WORKFLOW}.md").exists()

    def test_skill_reference_is_not_dangling(self):
        """Every workflow the emitted multiagent-orchestration SKILL.md names must
        itself be emitted, or the skill points at a file that does not exist."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build(root)
            skill = (
                root / ".claude" / "skills" / "multiagent-orchestration" / "SKILL.md"
            ).read_text()
            referenced = [
                name
                for name in (
                    _WORKFLOW,
                    "multi-agent-coordination",
                    "workflow-orchestration-patterns",
                )
                if name in skill
            ]
            assert referenced, "skill no longer names any composed workflow"
            missing = [
                name
                for name in referenced
                if not (root / ".claude" / "workflows" / f"{name}.md").exists()
            ]
            assert not missing, f"dangling workflow references: {missing}"
