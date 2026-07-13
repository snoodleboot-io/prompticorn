"""Per-tool write-layout strategies (PRO-60 / F2b).

Each supported builder has a :class:`ToolLayout` that owns how that tool's files
are laid out on disk (agent output, skills) and declares its capabilities
(subagents, workflows, rules, root-doc kind). This replaces the hardcoded
``if self.tool_name == ...`` branches that used to live in ``prompt_builder``.

Layouts are keyed by the *internal builder name* ("kilo", "cline", "claude",
"copilot", "cursor"). The two Kilo CLI ids both dispatch to the ``kilo`` builder
and produce identical output, so there is a single Kilo layout.
"""

import json
from pathlib import Path
from typing import Any

from prompticorn.builders.continue_builder import workflow_to_continue_prompt
from prompticorn.builders.gemini_builder import generate_gemini_settings, workflow_to_toml
from prompticorn.builders.junie_builder import slugify as junie_slugify
from prompticorn.builders.roo_builder import generate_roomodes
from prompticorn.builders.roo_builder import slugify as zed_slugify
from prompticorn.builders.skill_emitter import AGENTS_SKILLS_BASE, write_skill
from prompticorn.builders.windsurf_builder import workflow_to_windsurf


def _append_or_write(path: Path, content: Any) -> None:
    """Append to an existing concatenated file, or create it."""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
    else:
        path.write_text(str(content), encoding="utf-8")


class ToolLayout:
    """Base write-layout strategy. Subclasses define per-tool file placement."""

    #: Whether this tool emits subagents as separate files.
    writes_subagents: bool = False
    #: Whether this tool emits workflows as separate files.
    writes_workflows: bool = False
    #: Whether this tool writes core rules/convention files before agents.
    writes_rules: bool = False
    #: Whether the root doc is CLAUDE.md (True) or AGENTS.md (False).
    emits_claude_md: bool = False
    #: Whether to emit the root AGENTS.md at all. False for tools that carry
    #: their own convention files instead (e.g. Amazon Q's .amazonq/rules/).
    emits_agents_md: bool = True

    def root_doc_filename(self) -> str:
        return "CLAUDE.md" if self.emits_claude_md else "AGENTS.md"

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        raise NotImplementedError

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        raise NotImplementedError

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        """Write one workflow/command file. Only called when writes_workflows."""
        raise NotImplementedError

    def finalize(
        self, output: Path, built_agents: list[Any], config: dict[str, Any] | None
    ) -> list[str]:
        """Emit any aggregate file(s) built from all agents' outputs.

        Called once after every agent has been written. Base is a no-op; Roo
        overrides it to assemble the single ``.roomodes`` file.
        """
        return []


class KiloLayout(ToolLayout):
    """.kilo/ directory: per-agent files, subagents, workflows, rules."""

    writes_subagents = True
    writes_workflows = True
    writes_rules = True

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        agents_dir = output / ".kilo" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / f"{agent_name}.md").write_text(str(content), encoding="utf-8")
        return [f".kilo/agents/{agent_name}.md"]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".kilo", skill_name, content)]

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        commands_dir = output / ".kilo" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / f"{workflow_name}.md").write_text(content, encoding="utf-8")
        return [f".kilo/commands/{workflow_name}.md"]


class ClineLayout(ToolLayout):
    """.clinerules: single concatenated file."""

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        _append_or_write(output / ".clinerules", content)
        return [".clinerules"]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".cline", skill_name, content)]


class CursorLayout(ToolLayout):
    """.cursorrules: single concatenated file."""

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        _append_or_write(output / ".cursorrules", content)
        return [".cursorrules"]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".cursor", skill_name, content)]


class CopilotLayout(ToolLayout):
    """.github/copilot-instructions.md: concatenated; flat skill files."""

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        github_dir = output / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        _append_or_write(github_dir / "copilot-instructions.md", content)
        return [".github/copilot-instructions.md"]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        skills_dir = output / ".github" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / f"{skill_name}.md").write_text(content, encoding="utf-8")
        return [f".github/skills/{skill_name}.md"]


class ClaudeLayout(ToolLayout):
    """.claude/ directory: dict-of-files agent output, CLAUDE.md root doc."""

    emits_claude_md = True

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        # New format: content is a dict mapping relative file paths to markdown.
        if isinstance(content, dict) and all(
            isinstance(k, str) and isinstance(v, str) for k, v in content.items()
        ):
            written: list[str] = []
            for file_path_str, markdown_content in content.items():
                full_path = output / file_path_str
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(markdown_content, encoding="utf-8")
                written.append(file_path_str)
            return written

        # Old format (fallback): JSON dict to custom_instructions/.
        instructions_dir = output / "custom_instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        file_path = instructions_dir / f"{agent_name}.json"
        file_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        return [f"custom_instructions/{agent_name}.json"]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".claude", skill_name, content)]


class RooLayout(ToolLayout):
    """.roo/ + .roomodes: aggregate custom-modes file, per-mode rules, commands.

    Agents become entries in a single ``.roomodes`` (assembled in ``finalize``);
    each agent's bulk instructions go to ``.roo/rules-{slug}/`` (Roo loads those
    only when that mode is active). Conventions ride the root ``AGENTS.md``.
    """

    writes_workflows = True

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        # content is a RooBuilder mode-entry dict; write the bulk instructions
        # to the mode-specific rules dir and keep .roomodes lean.
        assert isinstance(content, dict)
        rules_dir = output / f".roo/rules-{content['slug']}"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rel = f".roo/rules-{content['slug']}/01-instructions.md"
        (output / rel).write_text(content["instructions"], encoding="utf-8")
        return [rel]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".roo", skill_name, content)]

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        commands_dir = output / ".roo" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / f"{workflow_name}.md").write_text(content, encoding="utf-8")
        return [f".roo/commands/{workflow_name}.md"]

    def finalize(
        self, output: Path, built_agents: list[Any], config: dict[str, Any] | None
    ) -> list[str]:
        mode_entries = [c for c in built_agents if isinstance(c, dict) and "slug" in c]
        if not mode_entries:
            return []
        (output / ".roomodes").write_text(generate_roomodes(mode_entries), encoding="utf-8")
        return [".roomodes"]


class JunieLayout(ToolLayout):
    """.junie/ directory: one agent file per agent, skills, and commands.

    Unlike Roo, Junie agents are one file each (``.junie/agents/<slug>.md``), so
    no aggregate ``finalize`` is needed. Conventions ride the root ``AGENTS.md``.
    """

    writes_workflows = True

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        agents_dir = output / ".junie" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        rel = f".junie/agents/{junie_slugify(agent_name)}.md"
        (output / rel).write_text(content, encoding="utf-8")
        return [rel]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".junie", skill_name, content)]

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        commands_dir = output / ".junie" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / f"{workflow_name}.md").write_text(content, encoding="utf-8")
        return [f".junie/commands/{workflow_name}.md"]


class ZedLayout(ToolLayout):
    """.agents/skills/ (Agent Skills spec) + AGENTS.md.

    Zed has no agent primitive, so each agent is emitted as a skill under
    ``.agents/skills/`` (alongside real skills); the routing overview and
    conventions ride the root ``AGENTS.md``.
    """

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        return [write_skill(output, AGENTS_SKILLS_BASE, zed_slugify(agent_name), content)]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, AGENTS_SKILLS_BASE, skill_name, content)]


class GeminiLayout(ToolLayout):
    """.gemini/ directory: one agent file per agent, skills, TOML commands.

    Agents are one file each (``.gemini/agents/<slug>.md``). Workflows become
    ``.gemini/commands/<slug>.toml``. ``finalize`` writes ``.gemini/settings.json``
    so Gemini reads the root ``AGENTS.md`` (E1) via ``context.fileName``.
    """

    writes_workflows = True

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        agents_dir = output / ".gemini" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        rel = f".gemini/agents/{junie_slugify(agent_name)}.md"
        (output / rel).write_text(content, encoding="utf-8")
        return [rel]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".gemini", skill_name, content)]

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        commands_dir = output / ".gemini" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        rel = f".gemini/commands/{junie_slugify(workflow_name)}.toml"
        (output / rel).write_text(workflow_to_toml(workflow_name, content), encoding="utf-8")
        return [rel]

    def finalize(
        self, output: Path, built_agents: list[Any], config: dict[str, Any] | None
    ) -> list[str]:
        gemini_dir = output / ".gemini"
        gemini_dir.mkdir(parents=True, exist_ok=True)
        (gemini_dir / "settings.json").write_text(generate_gemini_settings(), encoding="utf-8")
        return [".gemini/settings.json"]


class AmazonQLayout(ToolLayout):
    """.amazonq/ : JSON agents, rules conventions, saved prompts. No AGENTS.md.

    Amazon Q does not read AGENTS.md, so conventions are written to
    ``.amazonq/rules/`` (writes_rules) and no root doc is emitted. Agents are
    JSON (``.amazonq/cli-agents/``), workflows are prompts, skills are dropped
    (Amazon Q has no skill primitive).
    """

    writes_rules = True
    writes_workflows = True
    emits_agents_md = False

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        agents_dir = output / ".amazonq" / "cli-agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        rel = f".amazonq/cli-agents/{junie_slugify(agent_name)}.json"
        (output / rel).write_text(content, encoding="utf-8")
        return [rel]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        # Amazon Q has no skill primitive; skills are dropped in v1.
        return []

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        prompts_dir = output / ".amazonq" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        rel = f".amazonq/prompts/{junie_slugify(workflow_name)}.md"
        (output / rel).write_text(content, encoding="utf-8")
        return [rel]


class WindsurfLayout(ToolLayout):
    """.windsurf/ : agents-as-skills, rule conventions, workflows. No AGENTS.md.

    Agents (and real skills) go to ``.windsurf/skills/`` (escape the 12k rules
    budget); conventions go to ``.windsurf/rules/`` (writes_rules); workflows to
    ``.windsurf/workflows/``. The fat root AGENTS.md is suppressed for the char cap.
    """

    writes_rules = True
    writes_workflows = True
    emits_agents_md = False

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        return [write_skill(output, ".windsurf", zed_slugify(agent_name), content)]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        return [write_skill(output, ".windsurf", skill_name, content)]

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        workflows_dir = output / ".windsurf" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        rel = f".windsurf/workflows/{junie_slugify(workflow_name)}.md"
        (output / rel).write_text(workflow_to_windsurf(workflow_name, content), encoding="utf-8")
        return [rel]


class ContinueLayout(ToolLayout):
    """.continue/ : agents-as-rules, conventions rules, invokable prompts. No AGENTS.md.

    Continue has no agent primitive, so each agent is a description-scoped rule
    (``.continue/rules/<slug>.md``); conventions also go to ``.continue/rules/``
    (writes_rules); workflows become ``.continue/prompts/<slug>.md``. Skills are
    dropped (no primitive) and the root AGENTS.md is suppressed (not read).
    """

    writes_rules = True
    writes_workflows = True
    emits_agents_md = False

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        assert isinstance(content, str)
        rules_dir = output / ".continue" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rel = f".continue/rules/{junie_slugify(agent_name)}.md"
        (output / rel).write_text(content, encoding="utf-8")
        return [rel]

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        # Continue has no skill primitive; skills are dropped in v1.
        return []

    def write_workflow(self, output: Path, workflow_name: str, content: str) -> list[str]:
        prompts_dir = output / ".continue" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        rel = f".continue/prompts/{junie_slugify(workflow_name)}.md"
        (output / rel).write_text(
            workflow_to_continue_prompt(workflow_name, content), encoding="utf-8"
        )
        return [rel]


_LAYOUTS: dict[str, ToolLayout] = {
    "kilo": KiloLayout(),
    "cline": ClineLayout(),
    "cursor": CursorLayout(),
    "copilot": CopilotLayout(),
    "claude": ClaudeLayout(),
    "roo": RooLayout(),
    "junie": JunieLayout(),
    "zed": ZedLayout(),
    "gemini": GeminiLayout(),
    "amazonq": AmazonQLayout(),
    "windsurf": WindsurfLayout(),
    "continue": ContinueLayout(),
}


def get_layout(builder_name: str) -> ToolLayout:
    """Return the write-layout strategy for an internal builder name.

    Args:
        builder_name: Internal builder key (e.g. ``"kilo"``, ``"claude"``).

    Returns:
        The matching :class:`ToolLayout`.

    Raises:
        KeyError: If no layout is registered for ``builder_name``.
    """
    return _LAYOUTS[builder_name]
