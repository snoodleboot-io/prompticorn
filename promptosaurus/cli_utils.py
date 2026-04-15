"""Utility functions for CLI operations.

This module provides helper functions for CLI operations including:
    - Tool name normalization and validation
    - Supported tools listing

Constants:
    SUPPORTED_TOOLS: Set of supported AI tool names.
    TOOL_MAPPINGS: Mapping from normalized names to canonical names.

Functions:
    normalize_tool_name: Normalize user input to canonical tool name.
    validate_tool_name: Check if a tool is supported.
    get_supported_tools_display: Get formatted list of supported tools.
"""

import re
from typing import Final

SUPPORTED_TOOLS: Final[set[str]] = {"kilo-cli", "kilo-ide", "claude", "cline", "cursor", "copilot"}

# Mapping from normalized input (without special chars) to canonical tool name
TOOL_MAPPINGS: Final[dict[str, str]] = {
    "kilocli": "kilo-cli",
    "kiloide": "kilo-ide",
    "cline": "cline",
    "cursor": "cursor",
    "copilot": "copilot",
    "claude": "claude",
}


def normalize_tool_name(input_name: str) -> str:
    """Normalize tool name: remove special characters, convert to lowercase.

    This function takes user input (which may have various formats like
    "Kilo-CLI", "kilo_ide", "Cline", etc.) and normalizes it to the
    canonical tool name format.

    Args:
        input_name: The tool name input from user. Can include hyphens,
                   underscores, spaces, or mixed case.

    Returns:
        Normalized tool name in canonical format (e.g., 'kilo-cli').
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
        tool_name: The normalized tool name to validate.

    Returns:
        True if tool is in SUPPORTED_TOOLS, False otherwise.
    """
    return tool_name in SUPPORTED_TOOLS


def get_supported_tools_display() -> str:
    """Get comma-separated list of supported tools for error messages.

    Returns:
        Formatted string of supported tool names, sorted alphabetically.
    """
    return ", ".join(sorted(SUPPORTED_TOOLS))
