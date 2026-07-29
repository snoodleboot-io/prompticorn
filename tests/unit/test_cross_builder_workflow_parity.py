"""Every builder emits the workflows its agents are mapped to (PRO-139).

The workflow write loop gated on the *raw* IR agent's `.workflows`, which is empty
for most agents — workflows come from the mapping registry, not the IR model. So
every builder that writes workflows as separate files emitted only 13 of them.
Claude was unaffected: it emits workflows from inside the builder, against the
already-filtered agent.

This is the workflow-side counterpart of PRO-62, which fixed the same gating bug
for skills.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from prompticorn.prompt_builder import get_prompt_builder

_CONFIG = {
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
    "variant": "minimal",
}

# Builders whose layout sets ``writes_workflows``, with the directory each uses.
# Tools absent here (cline, cursor, copilot, zed, codex, aider, bedrock, kilo-cli)
# inline or omit workflows by design — `test_workflow_writing_builders_are_exactly`
# below pins that set so a layout flipping silently does not go unnoticed.
_WORKFLOW_BUILDERS = [
    ("kilo-ide", ".kilo/commands"),
    ("roo", ".roo/commands"),
    ("gemini", ".gemini/commands"),
    ("junie", ".junie/commands"),
    ("windsurf", ".windsurf/workflows"),
    ("continue", ".continue/prompts"),
    ("copilot-chat", ".github/prompts"),
    ("amazonq", ".amazonq/prompts"),
]

_ALL_TOOLS = [
    "claude",
    "kilo-ide",
    "kilo-cli",
    "roo",
    "gemini",
    "junie",
    "windsurf",
    "continue",
    "copilot-chat",
    "amazonq",
    "zed",
    "codex",
    "cline",
    "cursor",
    "copilot",
    "aider",
    "bedrock",
]

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_WORKFLOWS_DIR = _PROJECT_ROOT / "prompticorn" / "workflows"
_SKILLS_DIR = _PROJECT_ROOT / "prompticorn" / "skills"
_MAPPING = _PROJECT_ROOT / "prompticorn" / "configurations" / "agent_skill_mapping.yaml"

# Orchestrator coordination workflows. The user-visible symptom of the bug was an
# orchestrator agent whose workflows did not exist on disk outside Claude.
_ORCHESTRATOR_WORKFLOWS = {
    "async-workflow-execution",
    "multi-agent-coordination",
    "workflow-orchestration-patterns",
    "workflow-dependency-management",
    "workflow-error-handling-patterns",
    "task-breakdown",
}


def _emitted_workflow_names(root: Path, subdir: str) -> set[str]:
    """Emitted workflow names, with builder-specific suffixes stripped."""
    directory = root / subdir
    if not directory.exists():
        return set()
    return {
        path.name.removesuffix(".md").removesuffix(".prompt").removesuffix(".toml")
        for path in directory.iterdir()
        if path.is_file()
    }


def _build_and_collect(tool: str, subdir: str) -> set[str]:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        get_prompt_builder(tool).build(root, _CONFIG, dry_run=False)
        return _emitted_workflow_names(root, subdir)


@pytest.mark.unit
class TestMappingIntegrity:
    """A mapped name with no content behind it is a typo that silently ships."""

    def test_every_mapped_workflow_resolves_to_real_content(self):
        """These went unnoticed because the Claude builder falls back to a Jinja
        template and *fabricates* a stub, so the invented file looked like output.
        Two skills were listed under `workflows:` — `debugging-methodology` under
        `debug` and `architecture-documentation` under `architect`."""
        mapping = yaml.safe_load(_MAPPING.read_text())
        missing = sorted(
            {
                f"{agent}.workflows: {name}"
                for agent, entry in mapping.items()
                if isinstance(entry, dict)
                for name in (entry.get("workflows") or [])
                if not (_WORKFLOWS_DIR / name).is_dir()
            }
        )
        assert not missing, f"mapped workflows with no content: {missing}"

    def test_every_mapped_skill_resolves_to_real_content(self):
        mapping = yaml.safe_load(_MAPPING.read_text())
        missing = sorted(
            {
                f"{agent}.skills: {name}"
                for agent, entry in mapping.items()
                if isinstance(entry, dict)
                for name in (entry.get("skills") or [])
                if not (_SKILLS_DIR / name).is_dir()
            }
        )
        assert not missing, f"mapped skills with no content: {missing}"


@pytest.mark.unit
class TestCrossBuilderWorkflowParity:
    def test_workflow_writing_builders_are_exactly_the_expected_set(self):
        """Pin which layouts write workflows, so one flipping is a deliberate change."""
        actual = {t for t in _ALL_TOOLS if get_prompt_builder(t).layout.writes_workflows}
        assert actual == {tool for tool, _ in _WORKFLOW_BUILDERS}

    @pytest.mark.parametrize(("tool", "subdir"), _WORKFLOW_BUILDERS)
    def test_emits_at_least_what_claude_emits(self, tool, subdir):
        """The regression: every non-Claude builder carried 13 of the 32 workflows
        Claude emitted. No builder may silently carry less than the Claude
        realization."""
        claude = _build_and_collect("claude", ".claude/workflows")
        emitted = _build_and_collect(tool, subdir)
        missing = sorted(claude - emitted)
        assert not missing, f"{tool} is missing workflows Claude emits: {missing}"

    @pytest.mark.parametrize(("tool", "subdir"), _WORKFLOW_BUILDERS)
    def test_emits_orchestrator_workflows(self, tool, subdir):
        emitted = _build_and_collect(tool, subdir)
        missing = sorted(_ORCHESTRATOR_WORKFLOWS - emitted)
        assert not missing, f"{tool} is missing orchestrator workflows: {missing}"

    @pytest.mark.parametrize(("tool", "subdir"), _WORKFLOW_BUILDERS)
    def test_every_emitted_workflow_resolves_to_real_content(self, tool, subdir):
        """No builder invents a workflow file for a name with no content."""
        emitted = _build_and_collect(tool, subdir)
        invented = sorted(n for n in emitted if not (_WORKFLOWS_DIR / n).is_dir())
        assert not invented, f"{tool} emitted workflows with no source: {invented}"

    def test_claude_emits_no_invented_workflows(self):
        """Claude's template fallback fabricated a file for any mapped-but-missing
        workflow. With the mapping corrected there is nothing left to fabricate."""
        emitted = _build_and_collect("claude", ".claude/workflows")
        invented = sorted(n for n in emitted if not (_WORKFLOWS_DIR / n).is_dir())
        assert not invented, f"claude emitted workflows with no source: {invented}"

    @pytest.mark.parametrize(("tool", "subdir"), _WORKFLOW_BUILDERS)
    def test_emits_substantially_more_than_the_regression_count(self, tool, subdir):
        """Guards the specific regression: the buggy gate produced exactly 13."""
        emitted = _build_and_collect(tool, subdir)
        assert len(emitted) > 20, f"{tool} emitted only {len(emitted)} workflows"
