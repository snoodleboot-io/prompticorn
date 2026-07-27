"""OpenCodeBuilder for the Kilo Code CLI / OpenCode agent files (PRO-92).

OpenCode reads per-project agents from ``.opencode/agents/<name>.md`` — Markdown
files with YAML frontmatter, where the filename becomes the agent identifier —
and project rules from a root ``AGENTS.md``. Each agent file requires a
``description``; ``mode`` is ``primary`` or ``subagent``.

Skills are read by OpenCode through Claude-Code compatibility (``.claude/skills/``),
not from ``.opencode/``, so this builder emits agents and relies on the root
``AGENTS.md`` for conventions rather than inventing an ``.opencode/`` skill path.

Before PRO-92, ``kilo-cli`` dispatched to the ``kilo`` builder and emitted
``.kilo/`` — the documented ``.opencode/`` output never existed. This builder
implements it against the real format.

Verified against opencode.ai/docs/agents and opencode.ai/docs/rules. See PRO-92.
"""

import re

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.ir.models import Agent


def slugify(name: str) -> str:
    """Convert an agent name to an OpenCode agent slug (the filename == the id)."""
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    if not slug or not slug[0].isalpha():
        slug = f"agent-{slug}".strip("-")
    return slug or "agent"


class OpenCodeBuilder(Builder):
    """Builder for OpenCode agent files (YAML frontmatter + Markdown body)."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.opencode/agents/<slug>.md`` file body.

        Returns:
            YAML frontmatter (``description`` + ``mode``) followed by the system
            prompt. OpenCode takes the agent's identity from the filename, so no
            ``name`` field is emitted.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        frontmatter: dict[str, object] = {
            "description": agent.description,
            "mode": "primary",
        }
        fm_yaml = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
        return f"---\n{fm_yaml}\n---\n\n{agent.system_prompt}\n"

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for OpenCode (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the OpenCode output format."""
        return "OpenCode agent file (YAML frontmatter + Markdown)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "opencode"
