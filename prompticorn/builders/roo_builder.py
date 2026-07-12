"""RooBuilder for generating Roo Code configuration (PRO-34).

Roo represents agents as **custom modes** in a single aggregate ``.roomodes``
YAML file, so this builder returns a per-agent *mode entry* dict rather than a
file body. The lean identity (slug/name/roleDefinition/groups) goes into
``.roomodes``; the bulky agent prompt is written to ``.roo/rules-{slug}/`` by the
RooLayout (Roo loads those only when that mode is active). ``.roomodes`` itself
is assembled once by ``RooLayout.finalize``.

Verified against the Roo schema (packages/types/src/mode.ts, tool.ts). Required
mode fields: slug (``^[a-zA-Z0-9-]+$``), name, roleDefinition. groups values are
limited to read/edit/command/mcp/modes. See the Roo design doc in Linear.
"""

import re
from typing import Any

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.ir.models import Agent

# Substrings that indicate an agent needs a given Roo tool group.
_EDIT_HINTS = ("write", "edit", "create", "apply", "modify", "patch")
_COMMAND_HINTS = ("bash", "command", "shell", "execute", "run", "terminal")


def slugify(name: str) -> str:
    """Convert an agent name to a Roo-valid mode slug (``^[a-zA-Z0-9-]+$``)."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug or "mode"


def _groups_for(agent: Agent) -> list[str]:
    """Map an agent's tools to Roo tool groups (read/edit/command/mcp)."""
    tools = " ".join(agent.tools).lower()
    groups = ["read"]
    if not agent.tools or any(hint in tools for hint in _EDIT_HINTS):
        groups.append("edit")
    if not agent.tools or any(hint in tools for hint in _COMMAND_HINTS):
        groups.append("command")
    groups.append("mcp")
    return groups


class RooBuilder(Builder):
    """Builder for Roo Code custom modes.

    ``build`` returns a mode-entry dict consumed by RooLayout:
    ``{slug, name, roleDefinition, whenToUse, groups, instructions}``.
    """

    def build(
        self, agent: Agent, options: BuildOptions, config: dict | None = None
    ) -> dict[str, Any]:
        """Build a Roo mode entry for one agent.

        Args:
            agent: Agent IR model.
            options: Build options (variant, include flags).
            config: Optional project config.

        Returns:
            Mode-entry dict. ``instructions`` holds the full prompt for the
            mode's ``.roo/rules-{slug}/`` file; the rest populate ``.roomodes``.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        slug = slugify(agent.name)
        role_definition = f"You are the {agent.name} agent for this project. {agent.description}"

        # Bulk instructions live in .roo/rules-{slug}/; keep .roomodes lean.
        instruction_sections = [f"# {agent.name}", "", agent.system_prompt]
        if options.include_skills and agent.skills:
            instruction_sections += ["", "## Skills", "", *(f"- {s}" for s in agent.skills)]
        if options.include_workflows and agent.workflows:
            instruction_sections += ["", "## Workflows", "", *(f"- {w}" for w in agent.workflows)]
        instructions = "\n".join(instruction_sections).strip() + "\n"

        return {
            "slug": slug,
            "name": agent.name,
            "roleDefinition": role_definition,
            "whenToUse": agent.description,
            "groups": _groups_for(agent),
            "instructions": instructions,
        }

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Roo (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Roo output format."""
        return "Roo Code custom mode (.roomodes entry + .roo/rules-{slug}/)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "roo"


def generate_roomodes(mode_entries: list[dict[str, Any]]) -> str:
    """Serialize collected mode entries into ``.roomodes`` YAML.

    Emits only the lean identity fields (bulk instructions live in
    ``.roo/rules-{slug}/``). Field order is preserved (slug/name first) and
    ``groups`` is always present per the Roo schema.

    Args:
        mode_entries: Mode-entry dicts as returned by ``RooBuilder.build``.

    Returns:
        YAML text for the ``.roomodes`` file.
    """
    modes: list[dict[str, Any]] = []
    for entry in sorted(mode_entries, key=lambda e: e["slug"]):
        mode: dict[str, Any] = {
            "slug": entry["slug"],
            "name": entry["name"],
            "roleDefinition": entry["roleDefinition"],
        }
        if entry.get("whenToUse"):
            mode["whenToUse"] = entry["whenToUse"]
        mode["groups"] = entry["groups"]
        modes.append(mode)
    return yaml.safe_dump(
        {"customModes": modes},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
