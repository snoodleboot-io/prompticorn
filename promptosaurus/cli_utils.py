"""Utility functions for CLI operations."""

import re
from typing import Final

SUPPORTED_TOOLS: Final[set[str]] = {"kilo-cli", "kilo-ide", "cline", "cursor", "copilot"}

# Mapping from normalized input (without special chars) to canonical tool name
TOOL_MAPPINGS: Final[dict[str, str]] = {
    "kilocli": "kilo-cli",
    "kiloide": "kilo-ide",
    "cline": "cline",
    "cursor": "cursor",
    "copilot": "copilot",
}


def normalize_tool_name(input_name: str) -> str:
    """Normalize tool name: remove special characters, convert to lowercase.

    Args:
        input_name: The tool name input from user

    Returns:
        Normalized tool name

    Examples:
        >>> normalize_tool_name("Kilo-CLI")
        'kilo-cli'
        >>> normalize_tool_name("kilo_ide")
        'kilo-ide'
        >>> normalize_tool_name("Cline")
        'cline'
    """
    if not input_name:
        return ""

    # Remove all non-alphanumeric characters
    normalized = re.sub(r"[^a-zA-Z0-9]", "", input_name)

    # Convert to lowercase
    normalized = normalized.lower()

    # Look up canonical name
    return TOOL_MAPPINGS.get(normalized, normalized)


def validate_tool_name(tool_name: str) -> bool:
    """Check if tool name is supported.

    Args:
        tool_name: The normalized tool name

    Returns:
        True if tool is supported, False otherwise
    """
    return tool_name in SUPPORTED_TOOLS


def get_supported_tools_display() -> str:
    """Get comma-separated list of supported tools for error messages.

    Returns:
        Formatted string of supported tool names
    """
    return ", ".join(sorted(SUPPORTED_TOOLS))
