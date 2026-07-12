"""JunieBuilder for generating JetBrains Junie CLI configuration (PRO-38).

Junie CLI represents agents as one Markdown file per agent under
``.junie/agents/`` (YAML frontmatter + system-prompt body), so — unlike Roo's
aggregate ``.roomodes`` — this fits the per-agent write model directly. Skills
ride the E2 emitter (``.junie/skills/``), workflows go to ``.junie/commands/``,
and conventions ride the root ``AGENTS.md`` (E1), which Junie reads.

Verified against junie.jetbrains.com/docs (CLI, Beta). See the Junie design doc
in Linear.
"""

import re

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.ir.models import Agent

# Substrings indicating an agent needs a given Junie tool group.
_EDIT_HINTS = ("write", "edit", "create", "apply", "modify", "patch")
_COMMAND_HINTS = ("bash", "command", "shell", "execute", "run", "terminal")


def slugify(name: str) -> str:
    """Convert an agent name to a Junie agent slug (``[a-z][a-z0-9-]*``)."""
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    if not slug or not slug[0].isalpha():
        slug = f"agent-{slug}".strip("-")
    return slug or "agent"


def _junie_tools(agent: Agent) -> list[str]:
    """Map an agent's tools to Junie tool groups."""
    tools = " ".join(agent.tools).lower()
    groups = ["Read", "Grep", "Glob"]
    if not agent.tools or any(hint in tools for hint in _EDIT_HINTS):
        groups += ["Write", "Edit"]
    if not agent.tools or any(hint in tools for hint in _COMMAND_HINTS):
        groups.append("Bash")
    return groups


class JunieBuilder(Builder):
    """Builder for Junie CLI agent files (frontmatter + Markdown body)."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.junie/agents/<slug>.md`` file body.

        Returns:
            YAML frontmatter (name/description/tools[/skills]) + system prompt.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        frontmatter: dict[str, object] = {
            "name": slugify(agent.name),
            "description": agent.description,
            "tools": _junie_tools(agent),
        }
        if options.include_skills and agent.skills:
            frontmatter["skills"] = list(agent.skills)

        fm_yaml = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
        return f"---\n{fm_yaml}\n---\n\n{agent.system_prompt}\n"

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Junie (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Junie output format."""
        return "Junie CLI agent file (YAML frontmatter + Markdown)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "junie"
