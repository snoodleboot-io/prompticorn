"""Canonical AGENTS.md emitter (PRO-31 / E1).

Produces a self-contained root ``AGENTS.md``: an agent routing index plus the
inlined core/general conventions. This is the free baseline for every tool that
reads ``AGENTS.md`` natively (Codex, Zed, Windsurf, Roo, Junie; opt-in Gemini),
so it must not reference any single tool's private directory layout.
"""

from typing import Any

from prompticorn.builders.convention_generator import generate_core_convention


def generate_agents_md(
    primary_agents: list[dict] | None = None,
    *,
    repository_type: str = "",
    project: dict[str, Any] | None = None,
    primary_language: str = "",
    primary_spec: dict[str, Any] | None = None,
) -> str:
    """Generate self-contained ``AGENTS.md`` content.

    Args:
        primary_agents: List of dicts with ``name`` and ``description`` for each
            agent in scope. If falsy, a generic routing note is emitted instead
            of a table.
        repository_type: Repository type (e.g. ``single-language``), passed
            through to the core conventions.
        project: Project-level settings (commit_style, pr_size, deploy_target).
        primary_language: Primary project language, used for the source-tree
            layout in the core conventions.
        primary_spec: Primary folder/language spec, used to derive per-folder
            conventions (databases, data_access, error_handling, layout_style).

    Returns:
        Content for the root ``AGENTS.md`` file.
    """
    sections = [_generate_routing_index(primary_agents)]

    conventions = generate_core_convention(
        repository_type=repository_type,
        project=project,
        primary_language=primary_language,
        primary_spec=primary_spec,
    ).strip()
    if conventions:
        sections.append(conventions)

    return "\n\n---\n\n".join(sections) + "\n"


def _generate_routing_index(primary_agents: list[dict] | None) -> str:
    """Build the agent routing index (header + table or generic note)."""
    header = (
        "# Agents\n\n"
        "This file defines the AI agents available for this project and the "
        "conventions they follow. It is loaded automatically by tools that read "
        "`AGENTS.md`.\n"
    )

    if not primary_agents:
        return (
            header + "\n## Available agents\n\n"
            "Route to the agent whose purpose best matches the task, and switch "
            "agents as the task changes. Each agent has specialized behaviors and "
            "will suggest switching when another agent is better suited.\n"
        )

    rows = "\n".join(
        f"| **{a.get('name', 'unknown')}** | {_clean_description(a)} |" for a in primary_agents
    )
    return (
        header + f"\n## Available agents\n\n"
        f"This configuration includes the following {len(primary_agents)} "
        "primary agent(s). Route to the agent whose purpose best matches the "
        "task, and switch agents as the task changes.\n\n"
        "| Agent | Purpose |\n"
        "|-------|---------|\n"
        f"{rows}\n"
    )


def _clean_description(agent_info: dict) -> str:
    """Normalize an agent description for the routing table."""
    name = agent_info.get("name", "unknown")
    description = agent_info.get("description", f"Agent: {name}")

    # Drop a redundant "Agent: name" prefix if present.
    if description.startswith("Agent: "):
        description = description[7:].strip()

    # Capitalize the first letter for consistent table formatting.
    if description and description[0].islower():
        description = description[0].upper() + description[1:]

    return description
