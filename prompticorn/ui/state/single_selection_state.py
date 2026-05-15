"""Single selection state implementation.

This module provides the SingleSelectionState class for managing
single-option selection behavior (only one option can be selected at a time).

Classes:
    SingleSelectionState: Single selection state - immutable.
"""

from __future__ import annotations

from prompticorn.ui.state.selection_state import SelectionState


class SingleSelectionState(SelectionState):
    """Single selection state - immutable.

    This class implements the single selection behavior where only
    one option can be selected at a time. Navigation moves the
    selection cursor, and selecting an index updates the selection.

    The class uses an immutable pattern - all methods return new
    instances rather than modifying the existing state.

    Attributes:
        _selected: The currently selected index.
        _max: The maximum valid index.
    """

    def __init__(self, selected: int, max_index: int):
        """Initialize single selection state.

        Args:
            selected: The initially selected index.
            max_index: The maximum valid index (len(options) - 1).
        """
        self._selected = selected
        self._max = max_index

    @property
    def current_selection(self) -> int:
        """Get current selection.

        Returns:
            The currently selected index.
        """
        return self._selected

    def select(self, index: int) -> SingleSelectionState:
        """Return new state after selection.

        Sets the selection to the specified index if valid.

        Args:
            index: The index to select.

        Returns:
            New SingleSelectionState with the selection applied.
        """
        if 0 <= index <= self._max:
            return SingleSelectionState(index, self._max)
        return self

    def navigate(self, direction: int) -> SingleSelectionState:
        """Return new state after navigation.

        Moves the selection cursor by the specified direction.

        Args:
            direction: Navigation direction (-1 for up, +1 for down).

        Returns:
            New SingleSelectionState after navigation.
        """
        new_index = max(0, min(self._max, self._selected + direction))
        return SingleSelectionState(new_index, self._max)

    def is_selected(self, index: int) -> bool:
        """Check if index is selected.

        Args:
            index: The index to check.

        Returns:
            True if the index is currently selected.
        """
        return index == self._selected
