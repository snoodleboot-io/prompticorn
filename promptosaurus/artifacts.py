"""Artifact management for AI tool configuration files.

This module provides the ArtifactManager class for managing AI tool-specific
configuration artifacts. It tracks which files each AI tool creates and removes
when switching between tools.

The ARTIFACT_FILES constant defines:
    - Which files/directories each tool creates
    - Which files/directories should be removed when switching to another tool

This ensures clean transitions between different AI assistant configurations
without leaving orphaned files.

Classes:
    ArtifactManager: Manages AI tool artifact creation and removal.

Constants:
    ARTIFACT_FILES: Dictionary mapping tool names to their create/remove artifacts.
"""

import shutil
from pathlib import Path
from typing import Final

# Define which artifacts each tool creates and should remove when switching
ARTIFACT_FILES: Final[dict[str, dict[str, set[str]]]] = {
    "kilo-cli": {
        "create": {".opencode/"},
        "remove": {
            ".kilo/",  # Remove new kilo-ide output
            ".kilocode/",  # Remove legacy
            ".clinerules",
            ".cursor/",
            ".cursorrules",
            ".github/copilot-instructions.md",
        },
    },
    "kilo-ide": {
        "create": {".kilo/"},
        "remove": {
            ".opencode/",
            ".kilocode/",  # Remove legacy if present
            ".clinerules",
            ".cursor/",
            ".cursorrules",
            ".github/copilot-instructions.md",
        },
    },
    "cline": {
        "create": {".clinerules"},
        "remove": {
            ".opencode/",
            ".kilo/",
            ".kilocode/",
            ".cursor/",
            ".cursorrules",
            ".github/copilot-instructions.md",
        },
    },
    "cursor": {
        "create": {".cursor/", ".cursorrules"},
        "remove": {
            ".opencode/",
            ".kilo/",
            ".kilocode/",
            ".clinerules",
            ".github/copilot-instructions.md",
        },
    },
    "copilot": {
        "create": {".github/copilot-instructions.md"},
        "remove": {
            ".opencode/",
            ".kilo/",
            ".kilocode/",
            ".clinerules",
            ".cursor/",
            ".cursorrules",
        },
    },
}


class ArtifactManager:
    """Manage AI tool artifact creation and removal.

    This class handles cleaning up old AI tool artifacts when switching to a
    new tool, and provides information about what artifacts each tool creates.

    Attributes:
        base_path: Root path for artifact operations.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize the artifact manager.

        Args:
            base_path: Base path for artifact operations. Defaults to current directory.
        """
        self.base_path = base_path if base_path is not None else Path(".")

    def remove_artifacts(self, tool: str) -> list[str]:
        """Remove artifacts for a specific tool.

        Removes all artifact files/directories that the specified tool does NOT create,
        effectively cleaning up artifacts from other tools.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline', 'cursor').

        Returns:
            List of action messages describing what was removed.
            Empty list if tool is not recognized.

        Raises:
            OSError: If file/directory removal fails.
        """
        if tool not in ARTIFACT_FILES:
            return []

        to_remove = ARTIFACT_FILES[tool]["remove"]
        actions: list[str] = []

        for artifact in to_remove:
            artifact_path = self.base_path / artifact

            if artifact_path.exists():
                try:
                    if artifact_path.is_dir():
                        shutil.rmtree(artifact_path)
                        actions.append(f"Removed directory: {artifact}")
                    else:
                        artifact_path.unlink()
                        actions.append(f"Removed file: {artifact}")
                except OSError as e:
                    actions.append(f"Failed to remove {artifact}: {e}")

        return actions

    @property
    def current_tool(self) -> str | None:
        """Detect currently configured AI tool by checking which artifacts exist.

        Returns:
            The name of the currently active tool, or None if no tool detected.
            Returns the first matching tool found.
        """
        for tool, files in ARTIFACT_FILES.items():
            # Check if any of this tool's unique files exist
            for artifact in files["create"]:
                if (self.base_path / artifact).exists():
                    return tool

        return None

    def get_artifacts_to_create(self, tool: str) -> set[str]:
        """Get the set of artifacts that should be created for a tool.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline').

        Returns:
            Set of artifact paths to create. Empty set if tool not recognized.
        """
        if tool not in ARTIFACT_FILES:
            return set()
        return ARTIFACT_FILES[tool]["create"]

    def get_artifacts_to_remove(self, tool: str) -> set[str]:
        """Get the set of artifacts that should be removed for a tool.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline').

        Returns:
            Set of artifact paths to remove. Empty set if tool not recognized.
        """
        if tool not in ARTIFACT_FILES:
            return set()
        return ARTIFACT_FILES[tool]["remove"]
