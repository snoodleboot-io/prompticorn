"""The per-tool output files ``prompticorn switch`` creates and removes (PRO-141).

"Output" here means a generated configuration file on disk — ``.claude/``,
``.cursorrules``, ``AGENTS.md`` — the disposable side of the source/generated
wall. This module was called ``artifacts`` before ``prompticorn/artifact/``
existed, where an artifact is a *unit of release* with an id, a version and a
content hash. The two are unrelated, and the old name put them adjacent in
every file listing.

``TOOL_OUTPUT_FILES`` defines, per tool:
    - Which files/directories that tool creates
    - Which files/directories to remove when switching to it

Switching cleanly is the point: without the remove sets, a project that moved
from Cursor to Claude keeps serving stale ``.cursorrules`` to a tool that no
longer maintains it.

Classes:
    ToolOutputManager: Creates and removes per-tool output files.

Constants:
    TOOL_OUTPUT_FILES: Tool name to its create/remove output sets.
"""

import shutil
from pathlib import Path
from typing import Final

from prompticorn.tools import create_artifacts_by_tool

# The outputs each tool CREATES, sourced from the central tool registry
# (prompticorn/tools.py). A tool's `remove` set is derived from these (see
# _build_output_files), so adding a new tool means adding one ToolSpec entry
# and never touching another tool's configuration.
_TOOL_CREATE: Final[dict[str, set[str]]] = create_artifacts_by_tool()

# Legacy / never-valid outputs that must be cleaned up when switching to any
# tool, even though no current tool creates them (old output formats, and the
# root rules/ directory which must never exist).
_LEGACY_OUTPUTS: Final[frozenset[str]] = frozenset(
    {
        ".kilocode/",  # legacy kilo output directory
        "custom_instructions/",  # legacy format
        "rules/",  # ensure root rules/ never exists
    }
)


def _build_output_files() -> dict[str, dict[str, set[str]]]:
    """Derive the create/remove output map from the create sets.

    Each tool removes every OTHER tool's created outputs plus the shared legacy
    ones. A tool never removes its own. Because the remove sets are computed,
    they cannot drift out of sync with the create sets, and a new tool only
    needs a single entry in ``_TOOL_CREATE``.
    """
    output_files: dict[str, dict[str, set[str]]] = {}
    for tool, created in _TOOL_CREATE.items():
        remove: set[str] = set(_LEGACY_OUTPUTS)
        for other, other_created in _TOOL_CREATE.items():
            if other != tool:
                remove |= other_created
        # Never remove a path this tool also creates (some tools share create
        # paths, e.g. Codex and Zed both write .agents/); the tool keeps its own.
        remove -= set(created)
        output_files[tool] = {"create": set(created), "remove": remove}
    return output_files


# Which outputs each tool creates, and which it should remove when switching.
TOOL_OUTPUT_FILES: Final[dict[str, dict[str, set[str]]]] = _build_output_files()


class ToolOutputManager:
    """Create and remove the output files a given AI tool owns.

    Handles cleaning up another tool's outputs when switching, and reports
    which outputs a tool creates.

    Attributes:
        base_path: Root the output paths are resolved against.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize the manager.

        Args:
            base_path: Root the output paths are resolved against. Defaults to
                the current directory.
        """
        self.base_path = base_path if base_path is not None else Path(".")

    def remove_outputs_created_by(self, tool: str) -> list[str]:
        """Remove the outputs a specific tool created.

        When switching FROM a tool, remove what that tool CREATED.
        Use this when switching TO a new tool.

        Args:
            tool: The AI tool whose outputs to delete (e.g. 'kilo-ide', 'claude').

        Returns:
            Action messages describing what was removed. Empty if the tool is
            not recognized.

        Raises:
            OSError: If file/directory removal fails.
        """
        if tool not in TOOL_OUTPUT_FILES:
            return []

        to_remove = TOOL_OUTPUT_FILES[tool]["create"]
        actions: list[str] = []

        for output in to_remove:
            output_path = self.base_path / output

            if output_path.exists():
                try:
                    if output_path.is_dir():
                        import shutil

                        shutil.rmtree(output_path)
                        actions.append(f"Removed directory: {output}")
                    else:
                        output_path.unlink()
                        actions.append(f"Removed file: {output}")
                except Exception as e:
                    actions.append(f"Failed to remove {output}: {e}")

        return actions

    def remove_outputs(self, tool: str) -> list[str]:
        """Remove the outputs that belong to other tools.

        Removes every output the given tool does NOT create, which is what
        clears the previous tool's configuration on a switch.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline', 'cursor').

        Returns:
            Action messages describing what was removed. Empty if the tool is
            not recognized.

        Raises:
            OSError: If file/directory removal fails.
        """
        if tool not in TOOL_OUTPUT_FILES:
            return []

        to_remove = TOOL_OUTPUT_FILES[tool]["remove"]
        actions: list[str] = []

        for output in to_remove:
            output_path = self.base_path / output

            if output_path.exists():
                try:
                    if output_path.is_dir():
                        shutil.rmtree(output_path)
                        actions.append(f"Removed directory: {output}")
                    else:
                        output_path.unlink()
                        actions.append(f"Removed file: {output}")
                except OSError as e:
                    actions.append(f"Failed to remove {output}: {e}")

        return actions

    @property
    def current_tool(self) -> str | None:
        """Detect the currently configured AI tool from the outputs on disk.

        Returns the tool with the MOST created outputs present on disk (ties
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
        for tool, files in TOOL_OUTPUT_FILES.items():
            count = sum(1 for output in files["create"] if (self.base_path / output).exists())
            if count > best_count:
                best_tool, best_count = tool, count
        return best_tool

    def outputs_to_create(self, tool: str) -> set[str]:
        """The outputs a tool should create.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline').

        Returns:
            Output paths to create. Empty if the tool is not recognized.
        """
        if tool not in TOOL_OUTPUT_FILES:
            return set()
        return TOOL_OUTPUT_FILES[tool]["create"]

    def outputs_to_remove(self, tool: str) -> set[str]:
        """The outputs a tool should remove.

        Args:
            tool: The AI tool name (e.g., 'kilo-cli', 'cline').

        Returns:
            Output paths to remove. Empty if the tool is not recognized.
        """
        if tool not in TOOL_OUTPUT_FILES:
            return set()
        return TOOL_OUTPUT_FILES[tool]["remove"]
