"""GeminiBuilder for generating Google Gemini CLI configuration (PRO-45).

Gemini CLI represents agents as one Markdown file per agent under
``.gemini/agents/`` (YAML frontmatter + system-prompt body) — the per-agent
write model, like Junie. Skills ride the E2 emitter (``.gemini/skills/``),
workflows become ``.gemini/commands/<name>.toml``, and conventions ride the root
``AGENTS.md`` (E1) pointed at via a generated ``.gemini/settings.json``
(``context.fileName``), since Gemini reads ``GEMINI.md`` by default.

Verified against github.com/google-gemini/gemini-cli. v1 emits only name +
description frontmatter (the agent frontmatter contract is recent/evolving).
See the Gemini design doc in Linear.
"""

import json

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.junie_builder import slugify
from prompticorn.ir.models import Agent


class GeminiBuilder(Builder):
    """Builder for Gemini CLI agent files (frontmatter + Markdown body)."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.gemini/agents/<slug>.md`` file body.

        Returns:
            YAML frontmatter (name/description) + the agent's system prompt.
            ``tools`` is omitted so the subagent inherits all tools (the
            frontmatter tool contract is version-sensitive).
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        description = " ".join(agent.description.split())
        frontmatter = yaml.safe_dump(
            {"name": slugify(agent.name), "description": description},
            sort_keys=False,
            allow_unicode=True,
        ).strip()
        return f"---\n{frontmatter}\n---\n\n{agent.system_prompt}\n"

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Gemini (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Gemini output format."""
        return "Gemini CLI agent file (.gemini/agents/<name>.md)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "gemini"


def generate_gemini_settings() -> str:
    """Return ``.gemini/settings.json`` content pointing Gemini at AGENTS.md.

    Gemini CLI reads ``GEMINI.md`` by default; this makes it also read the
    prompticorn-generated root ``AGENTS.md`` via ``context.fileName``.
    """
    import json

    return json.dumps({"context": {"fileName": "AGENTS.md"}}, indent=2) + "\n"


def workflow_to_toml(workflow_name: str, content: str) -> str:
    """Wrap a workflow's Markdown body into a Gemini command TOML file.

    Emits both fields as TOML basic strings via ``json.dumps`` — JSON string
    syntax is a valid TOML basic string, so it correctly escapes any content
    (quotes, backslashes, newlines, and ``'''`` sequences). A hand-built ``'''``
    literal could not: TOML literal strings cannot contain ``'''`` and do not
    support escaping, so a workflow body with a triple-quote produced invalid
    TOML (PRO-88).
    """
    description = f"{workflow_name} workflow"
    return f"description = {json.dumps(description)}\nprompt = {json.dumps(content)}\n"
