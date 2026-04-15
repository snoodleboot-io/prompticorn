"""Generator for root AGENTS.md file with only in-scope agents."""


def generate_agents_md(primary_agents: list[dict] | None = None) -> str:
    """Generate AGENTS.md content with only the agents in scope.

    Args:
        primary_agents: List of dicts with 'name' and 'description' for each agent in scope.
                       If None, generates a template.

    Returns:
        Content for root AGENTS.md file
    """

    # If no agents provided, generate template
    if not primary_agents:
        return _generate_template()

    # Generate with actual agents in scope
    return _generate_with_agents(primary_agents)


def _generate_template() -> str:
    """Generate template AGENTS.md when no agents are specified."""
    return """# Kilo Code Agents

This directory contains the agent instructions and system configuration.

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.kilo/rules/`** — Core behaviors and conventions (always loaded)
- **`.kilo/agents/`** — Individual agent definitions and subagents

## Core Instructions

The `.kilo/rules/` directory contains core files that are always loaded:
- `system.md` — Core system behaviors
- `conventions.md` — General conventions
- `session.md` — Session management
- `conventions-{language}.md` — Language-specific conventions (if configured)

**Important:** Always load the core files from `.kilo/rules/` for any task, as they contain the foundational behaviors and conventions for this project.

## Available Agents

This configuration includes multiple agent types. See `.kilo/agents/` for all available agents.

## Usage

Switch between agents based on the task at hand. Each agent has specialized behaviors and will suggest switching when appropriate.

## Configuration

The IDE extensions automatically load the appropriate agent instructions from the `.kilo/` directory based on the current mode selection.

For other tools (Claude, Cline, Cursor, Copilot), the agent instructions are adapted to that tool's format but maintain the same structure and purpose.
"""


def _generate_with_agents(primary_agents: list[dict]) -> str:
    """Generate AGENTS.md with specific agents in scope."""

    # Build agent table rows
    agent_rows = []
    for agent_info in primary_agents:
        name = agent_info.get("name", "unknown")
        description = agent_info.get("description", f"Agent: {name}")

        # Clean up description - remove "Agent: name" prefix if it exists
        if description.startswith("Agent: "):
            description = description[7:].strip()

        # Capitalize first letter if needed
        if description and description[0].islower():
            description = description[0].upper() + description[1:]

        # Format for markdown table
        agent_rows.append(f"| **{name}** | {description} |")

    agent_table = "\n".join(agent_rows)

    return f"""# Kilo Code Agents

This directory contains the agent instructions and system configuration for your project.

## In-Scope Agents

This configuration includes the following {len(primary_agents)} primary agent(s):

| Agent | Purpose |
|-------|---------|
{agent_table}

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents in scope
- **`.kilo/rules/`** — Core behaviors and conventions (always loaded)
- **`.kilo/agents/`** — Agent definitions and subagents

## Core Instructions

The `.kilo/rules/` directory contains core files that are always loaded:
- `system.md` — Core system behaviors
- `conventions.md` — General conventions
- `session.md` — Session management
- `conventions-{{language}}.md` — Language-specific conventions (if configured)

**Important:** Always load the core files from `.kilo/rules/` for any task, as they contain the foundational behaviors and conventions for this project.

## Usage

Switch between agents based on the task at hand. Each agent has specialized behaviors and will suggest switching when appropriate.

## Configuration

The IDE extensions automatically load the appropriate agent instructions from the `.kilo/` directory based on the current mode selection.

For other tools (Claude, Cline, Cursor, Copilot), the agent instructions are adapted to that tool's format but maintain the same structure and purpose.
"""
