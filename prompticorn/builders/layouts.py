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

from prompticorn.builders.skill_emitter import write_skill


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

    def root_doc_filename(self) -> str:
        return "CLAUDE.md" if self.emits_claude_md else "AGENTS.md"

    def write_agent(self, output: Path, agent_name: str, content: str | dict[str, Any]) -> list[str]:
        raise NotImplementedError

    def write_skill(self, output: Path, skill_name: str, content: str) -> list[str]:
        raise NotImplementedError


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


_LAYOUTS: dict[str, ToolLayout] = {
    "kilo": KiloLayout(),
    "cline": ClineLayout(),
    "cursor": CursorLayout(),
    "copilot": CopilotLayout(),
    "claude": ClaudeLayout(),
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
