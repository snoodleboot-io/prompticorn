"""Unit tests for artifact map derivation (PRO-29 / F1).

The remove sets in ARTIFACT_FILES are derived from the per-tool create sets
plus shared legacy artifacts, rather than hand-maintained. These tests lock in
that invariant so the O(n^2) hand-maintenance cannot creep back, and so adding
a new tool provably never requires editing another tool's configuration.
"""

import unittest

from prompticorn.artifacts import (
    _LEGACY_ARTIFACTS,
    _TOOL_CREATE,
    ARTIFACT_FILES,
    _build_artifact_files,
)


class TestArtifactDerivation(unittest.TestCase):
    """Verify remove sets are correctly derived from create sets."""

    def test_tools_match_create_source(self) -> None:
        """ARTIFACT_FILES exposes exactly the tools defined in _TOOL_CREATE."""
        self.assertEqual(set(ARTIFACT_FILES), set(_TOOL_CREATE))

    def test_create_sets_preserved(self) -> None:
        """Each tool's create set is exactly its _TOOL_CREATE entry."""
        for tool, created in _TOOL_CREATE.items():
            self.assertEqual(ARTIFACT_FILES[tool]["create"], created)

    def test_remove_is_union_of_other_creates_plus_legacy(self) -> None:
        """remove(tool) == (union of other tools' creates) | legacy."""
        for tool in _TOOL_CREATE:
            expected = set(_LEGACY_ARTIFACTS)
            for other, created in _TOOL_CREATE.items():
                if other != tool:
                    expected |= created
            self.assertEqual(ARTIFACT_FILES[tool]["remove"], expected)

    def test_tool_never_removes_its_own_artifacts(self) -> None:
        """A tool's create and remove sets are disjoint."""
        for tool, created in _TOOL_CREATE.items():
            self.assertEqual(created & ARTIFACT_FILES[tool]["remove"], set())

    def test_every_create_is_removed_by_every_other_tool(self) -> None:
        """Switching to any other tool cleans up this tool's artifacts."""
        for tool, created in _TOOL_CREATE.items():
            for other in _TOOL_CREATE:
                if other != tool:
                    self.assertTrue(
                        created <= ARTIFACT_FILES[other]["remove"],
                        f"{other} does not remove {tool}'s artifacts {created}",
                    )

    def test_legacy_artifacts_removed_by_all_tools(self) -> None:
        """Legacy artifacts are cleaned up regardless of the active tool."""
        for tool in _TOOL_CREATE:
            self.assertTrue(_LEGACY_ARTIFACTS <= ARTIFACT_FILES[tool]["remove"])

    def test_adding_a_tool_needs_no_other_edits(self) -> None:
        """A new tool entry derives cleanly without touching existing tools.

        Simulates registering a hypothetical tool by extending only the create
        source, and asserts existing tools automatically learn to remove it.
        """
        extended = dict(_TOOL_CREATE)
        extended["newtool"] = {".newtool/"}
        # Re-derive using the same logic against the extended source.
        derived: dict[str, dict[str, set[str]]] = {}
        for tool, created in extended.items():
            remove = set(_LEGACY_ARTIFACTS)
            for other, other_created in extended.items():
                if other != tool:
                    remove |= other_created
            derived[tool] = {"create": set(created), "remove": remove}

        # Every pre-existing tool now removes the new tool's artifact...
        for tool in _TOOL_CREATE:
            self.assertIn(".newtool/", derived[tool]["remove"])
        # ...and the new tool removes every existing tool's artifacts.
        for created in _TOOL_CREATE.values():
            self.assertTrue(created <= derived["newtool"]["remove"])

    def test_build_is_deterministic(self) -> None:
        """_build_artifact_files produces equal maps on repeated calls."""
        self.assertEqual(_build_artifact_files(), _build_artifact_files())


if __name__ == "__main__":
    unittest.main()
