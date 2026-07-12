"""ZedBuilder for generating Zed agent configuration (PRO-41).

Zed has no custom-agent/persona primitive — its agent reads Instructions
(``AGENTS.md``, via E1) and Skills. So each prompticorn agent is emitted as a
**skill** (``.agents/skills/<slug>/SKILL.md``: YAML frontmatter + system-prompt
body), and real skills land in the same directory (E2). The always-on routing
overview + conventions ride the root ``AGENTS.md``.

Verified against zed.dev/docs/ai/{instructions,skills}. See the Zed design doc
in Linear.
"""

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.roo_builder import slugify
from prompticorn.ir.models import Agent

# Zed caps the total skill catalog (names + descriptions) at ~50KB, so keep each
# agent-as-skill description to a single tight line.
_MAX_DESCRIPTION = 500


class ZedBuilder(Builder):
    """Builder for Zed agent-as-skill files (frontmatter + Markdown body)."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.agents/skills/<slug>/SKILL.md`` body for an agent.

        Returns:
            YAML frontmatter (name/description) + the agent's system prompt.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        description = " ".join(agent.description.split())
        if len(description) > _MAX_DESCRIPTION:
            description = description[: _MAX_DESCRIPTION - 1].rstrip() + "…"

        frontmatter = yaml.safe_dump(
            {"name": slugify(agent.name), "description": description},
            sort_keys=False,
            allow_unicode=True,
        ).strip()
        return f"---\n{frontmatter}\n---\n\n{agent.system_prompt}\n"

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Zed (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Zed output format."""
        return "Zed agent-as-skill file (.agents/skills/<name>/SKILL.md)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "zed"
