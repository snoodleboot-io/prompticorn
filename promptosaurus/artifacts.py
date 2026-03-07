"""Artifact management for AI tool configuration files."""

import shutil
from pathlib import Path
from typing import Final

# Define which artifacts each tool creates and should remove when switching
ARTIFACT_FILES: Final[dict[str, dict[str, set[str]]]] = {
    "kilo-cli": {
        "create": {".opencode/"},
        "remove": {
            ".kilocode/",
            ".clinerules",
            ".cursor/",
            ".cursorrules",
            ".github/copilot-instructions.md",
        },
    },
    "kilo-ide": {
        "create": {".kilocode/"},
        "remove": {
            ".opencode/",
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
            ".kilocode/",
            ".clinerules",
            ".github/copilot-instructions.md",
        },
    },
    "copilot": {
        "create": {".github/copilot-instructions.md"},
        "remove": {
            ".opencode/",
            ".kilocode/",
            ".clinerules",
            ".cursor/",
            ".cursorrules",
        },
    },
}


class ArtifactManager:
    """Manage AI tool artifact creation and removal."""

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize the artifact manager.

        Args:
            base_path: Base path for artifact operations. Defaults to current directory.
        """
        self.base_path = base_path if base_path is not None else Path(".")

    def remove_artifacts(self, tool: str) -> list[str]:
        """Remove artifacts for a specific tool.

        Args:
            tool: The AI tool name

        Returns:
            List of action messages describing what was removed
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

    def get_current_tool(self) -> str | None:
        """Detect currently configured AI tool by checking which artifacts exist.

        Returns:
            The name of the currently active tool, or None if no tool detected
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
            tool: The AI tool name

        Returns:
            Set of artifact paths to create
        """
        if tool not in ARTIFACT_FILES:
            return set()
        return ARTIFACT_FILES[tool]["create"]

    def get_artifacts_to_remove(self, tool: str) -> set[str]:
        """Get the set of artifacts that should be removed for a tool.

        Args:
            tool: The AI tool name

        Returns:
            Set of artifact paths to remove
        """
        if tool not in ARTIFACT_FILES:
            return set()
        return ARTIFACT_FILES[tool]["remove"]
