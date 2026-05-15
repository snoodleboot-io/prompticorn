"""Naming utilities for file name conversion.

This module provides utilities for converting agent/subagent names to file names
following different naming conventions (kebab-case, snake_case, etc.).
"""

import re


def to_kebab_case(name: str) -> str:
    """Convert a name to kebab-case.

    Examples:
        "Code Agent" -> "code-agent"
        "code_agent" -> "code-agent"
        "CodeAgent" -> "code-agent"
        "Feature Implementation" -> "feature-implementation"

    Args:
        name: The name to convert

    Returns:
        The kebab-case version of the name
    """
    # Replace underscores and spaces with hyphens
    name = name.replace("_", "-").replace(" ", "-")

    # Insert hyphens before uppercase letters (for CamelCase)
    name = re.sub(r"([a-z])([A-Z])", r"\1-\2", name)

    # Convert to lowercase
    name = name.lower()

    # Remove multiple consecutive hyphens
    name = re.sub(r"-+", "-", name)

    # Remove leading/trailing hyphens
    name = name.strip("-")

    return name


def agent_to_file_name(agent_name: str) -> str:
    """Convert agent name to agent file name.

    Examples:
        "code" -> "code-agent"
        "frontend" -> "frontend-agent"
        "orchestrator" -> "orchestrator-agent"

    Args:
        agent_name: The agent name

    Returns:
        The agent file name (kebab-case with -agent suffix)
    """
    base = to_kebab_case(agent_name)
    if not base.endswith("-agent"):
        return f"{base}-agent"
    return base


def subagent_to_file_name(subagent_name: str) -> str:
    """Convert subagent name to subagent file name.

    Examples:
        "code-reviewer" -> "code-reviewer"
        "Code Reviewer" -> "code-reviewer"
        "review/code" -> "code-reviewer"
        "debug/rubber-duck" -> "rubber-duck"

    Args:
        subagent_name: The subagent name

    Returns:
        The subagent file name (kebab-case)
    """
    # Handle paths like "review/code" -> "code-reviewer"
    if "/" in subagent_name:
        parts = subagent_name.split("/")
        category = parts[0]  # e.g., "review"
        name = parts[1]  # e.g., "code"
        # For some patterns, append the category
        if category in ["review", "debug", "code"]:
            return to_kebab_case(f"{name}-{category}er")
        else:
            return to_kebab_case(name)

    return to_kebab_case(subagent_name)


def workflow_to_file_name(workflow_name: str) -> str:
    """Convert workflow name to workflow file name.

    Examples:
        "feature" -> "feature-implementation"
        "Feature Implementation" -> "feature-implementation"
        "code-review" -> "code-review"

    Args:
        workflow_name: The workflow name

    Returns:
        The workflow file name (kebab-case)
    """
    return to_kebab_case(workflow_name)


def skill_to_directory_name(skill_name: str) -> str:
    """Convert skill name to skill directory name.

    Examples:
        "Feature Planning" -> "feature-planning"
        "feature_planning" -> "feature-planning"
        "post-implementation-checklist" -> "post-implementation-checklist"

    Args:
        skill_name: The skill name

    Returns:
        The skill directory name (kebab-case)
    """
    return to_kebab_case(skill_name)
