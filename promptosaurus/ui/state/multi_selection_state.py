"""Multi-selection state implementation.

This module provides the MultiSelectionState class for managing
multi-option selection behavior (multiple options can be selected simultaneously).

Classes:
    MultiSelectionState: Multi-selection state - allows selecting multiple options.
"""

from __future__ import annotations

from promptosaurus.ui.state.selection_state import SelectionState


class MultiSelectionState(SelectionState):
    """Multi-selection state - allows selecting multiple options.

    This class implements the standard multi-select behavior where users
    can freely select or deselect any number of options without any
    mutual exclusion constraints.

    The class uses an immutable pattern - all methods return new
    instances rather than modifying the existing state.

    Attributes:
        _selected: Frozenset of selected indices.
        _max: The maximum valid index.
    """

    def __init__(self, selected: set[int], max_index: int):
        """Initialize multi-selection state.

        Args:
            selected: Set of initially selected indices.
            max_index: The maximum valid index (len(options) - 1).
        """
        self._selected = frozenset(selected)
        self._max = max_index

    @property
    def current_selection(self) -> set[int]:
        """Get current selections.

        Returns:
            Set of currently selected indices.
        """
        return set(self._selected)

    def select(self, index: int) -> MultiSelectionState:
        """Toggle selection at index.

        If the index is already selected, it will be deselected.
        If not selected, it will be added to the selection.

        Args:
            index: The index to toggle.

        Returns:
            New MultiSelectionState with the toggle applied.
        """
        if index > self._max:
            return self

        new_selected = set(self._selected)
        if index in new_selected:
            new_selected.remove(index)
        else:
            new_selected.add(index)
        return MultiSelectionState(new_selected, self._max)

    def navigate(self, direction: int) -> MultiSelectionState:
        """Multi-select doesn't use navigation - returns self.

        In multi-select mode, arrow keys are not used for navigation
        since there's no single "current" selection to move around.

        Args:
            direction: Ignored (no navigation in multi-select).

        Returns:
            The same state instance (no change).
        """
        return self

    def is_selected(self, index: int) -> bool:
        """Check if index is selected.

        Args:
            index: The index to check.

        Returns:
            True if the index is currently selected.
        """
        return index in self._selected
