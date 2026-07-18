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

from prompticorn.tools import create_artifacts_by_tool

# The artifacts each tool CREATES, sourced from the central tool registry
# (prompticorn/tools.py). A tool's `remove` set is derived from these (see
# _build_artifact_files), so adding a new tool means adding one ToolSpec entry
# and never touching another tool's configuration.
_TOOL_CREATE: Final[dict[str, set[str]]] = create_artifacts_by_tool()

# Legacy / never-valid artifacts that must be cleaned up when switching to any
# tool, even though no current tool creates them (old output formats, and the
# root rules/ directory which must never exist).
_LEGACY_ARTIFACTS: Final[frozenset[str]] = frozenset(
    {
        ".kilocode/",  # legacy kilo output directory
        "custom_instructions/",  # legacy format
        "rules/",  # ensure root rules/ never exists
    }
)


def _build_artifact_files() -> dict[str, dict[str, set[str]]]:
    """Derive the create/remove artifact map from the create sets.

    Each tool removes every OTHER tool's created artifacts plus the shared
    legacy artifacts. A tool never removes its own artifacts. Because the
    remove sets are computed, they cannot drift out of sync with the create
    sets, and a new tool only needs a single entry in ``_TOOL_CREATE``.
    """
    artifact_files: dict[str, dict[str, set[str]]] = {}
    for tool, created in _TOOL_CREATE.items():
        remove: set[str] = set(_LEGACY_ARTIFACTS)
        for other, other_created in _TOOL_CREATE.items():
            if other != tool:
                remove |= other_created
        # Never remove a path this tool also creates (some tools share create
        # paths, e.g. Codex and Zed both write .agents/); the tool keeps its own.
        remove -= set(created)
        artifact_files[tool] = {"create": set(created), "remove": remove}
    return artifact_files


# Define which artifacts each tool creates and should remove when switching.
ARTIFACT_FILES: Final[dict[str, dict[str, set[str]]]] = _build_artifact_files()


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

    def remove_artifacts_created_by(self, tool: str) -> list[str]:
        """Remove artifacts created by a specific tool.

        When switching FROM a tool, remove what that tool CREATED.
        Use this when switching TO a new tool.

        Args:
            tool: The AI tool name to clean up after (e.g., 'kilo-ide', 'claude').

        Returns:
            List of action messages describing what was removed.
            Empty list if tool is not recognized.

        Raises:
            OSError: If file/directory removal fails.
        """
        if tool not in ARTIFACT_FILES:
            return []

        to_remove = ARTIFACT_FILES[tool]["create"]
        actions: list[str] = []

        for artifact in to_remove:
            artifact_path = self.base_path / artifact

            if artifact_path.exists():
                try:
                    if artifact_path.is_dir():
                        import shutil

                        shutil.rmtree(artifact_path)
                        actions.append(f"Removed directory: {artifact}")
                    else:
                        artifact_path.unlink()
                        actions.append(f"Removed file: {artifact}")
                except Exception as e:
                    actions.append(f"Failed to remove {artifact}: {e}")

        return actions

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
        """Detect the currently configured AI tool by which artifacts exist.

        Returns the tool with the MOST create-artifacts present on disk (ties
        broken by registration order). This "most-specific match" distinguishes
        tools whose create sets overlap: e.g. Codex writes both ``.agents/`` and
        ``.codex/`` while Zed writes only ``.agents/``, so a Codex project (both
        present) resolves to Codex, and a Zed project (only ``.agents/``) to Zed.
        For the disjoint-create tools this behaves exactly like a first match.

        Returns:
            The name of the currently active tool, or None if none detected.
        """
        best_tool: str | None = None
        best_count = 0
        for tool, files in ARTIFACT_FILES.items():
            count = sum(
                1 for artifact in files["create"] if (self.base_path / artifact).exists()
            )
            if count > best_count:
                best_tool, best_count = tool, count
        return best_tool

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
