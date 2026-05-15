"""Generator for CLAUDE.md routing file."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from prompticorn.builders.naming_utils import agent_to_file_name


def generate_claude_md(primary_agents: list[dict], persona_name: str = "software_engineer") -> str:
    """Generate CLAUDE.md content with agent routing table.

    Args:
        primary_agents: List of dicts with 'name' and 'description' for each agent
        persona_name: Name of the persona (e.g., "software_engineer")

    Returns:
        Content for root CLAUDE.md file
    """
    # Load template
    template_dir = Path(__file__).parent.parent / "templates" / "claude"
    jinja_env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template("CLAUDE.md.j2")

    # Prepare agent data
    agents_data = []
    for agent_info in primary_agents:
        name = agent_info.get("name", "unknown")
        description = agent_info.get("description", f"Agent: {name}")

        # Clean up description
        if description.startswith("Agent: "):
            description = description[7:].strip()
        if description and description[0].islower():
            description = description[0].upper() + description[1:]

        agents_data.append(
            {
                "name": name,
                "description": description,
                "file_name": agent_to_file_name(name),
            }
        )

    # Generate routing categories
    routing_categories = _generate_routing_categories()

    # Render template
    return template.render(
        last_updated=datetime.now().strftime("%Y-%m-%d"),
        agent_count=len(primary_agents),
        persona_name=persona_name.replace("_", " ").title(),
        agents=agents_data,
        routing_categories=routing_categories,
    )


def _generate_routing_categories() -> list[dict]:
    """Generate routing rules by category.

    Returns:
        List of routing category dictionaries
    """
    return [
        {
            "name": "Code Implementation",
            "keywords": '"write", "implement", "create", "build", "add feature"',
            "agent": "code-agent",
        },
        {
            "name": "System Design",
            "keywords": '"design", "architect", "plan system", "design database"',
            "agent": "architect-agent",
        },
        {
            "name": "Bug Fixing",
            "keywords": '"debug", "fix bug", "not working", "error", "failing"',
            "agent": "debug-agent",
        },
        {
            "name": "Code Review",
            "keywords": '"review", "check code", "audit", "assess quality"',
            "agent": "review-agent",
        },
        {
            "name": "Testing",
            "keywords": '"test", "write tests", "coverage", "test suite"',
            "agent": "test-agent",
        },
        {
            "name": "Refactoring",
            "keywords": '"refactor", "improve code", "clean up", "restructure"',
            "agent": "refactor-agent",
        },
        {
            "name": "Performance",
            "keywords": '"optimize", "performance", "slow", "speed up", "benchmark"',
            "agent": "performance-agent",
        },
        {
            "name": "Frontend Development",
            "keywords": '"UI", "interface", "frontend", "component", "accessibility"',
            "agent": "frontend-agent",
        },
        {
            "name": "Backend Development",
            "keywords": '"API", "backend", "microservice", "database", "server"',
            "agent": "backend-agent",
        },
        {
            "name": "Documentation",
            "keywords": '"document", "explain", "write docs", "README"',
            "agent": "explain-agent",
        },
        {
            "name": "Questions",
            "keywords": '"how does", "what is", "explain", "why"',
            "agent": "ask-agent",
        },
        {
            "name": "Multi-step Workflows",
            "keywords": '"coordinate", "manage", "orchestrate", "complex task"',
            "agent": "orchestrator-agent",
        },
        {
            "name": "Planning",
            "keywords": '"plan", "PRD", "requirements", "design document"',
            "agent": "plan-agent",
        },
        {
            "name": "Code Standards",
            "keywords": '"enforce", "standards", "coding style", "check compliance"',
            "agent": "enforcement-agent",
        },
        {
            "name": "Migrations",
            "keywords": '"migrate", "upgrade", "update dependencies", "framework migration"',
            "agent": "migration-agent",
        },
    ]
