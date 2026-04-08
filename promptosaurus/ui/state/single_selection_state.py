"""Single selection state implementation.

This module provides the SingleSelectionState class for managing
single-option selection behavior (only one option can be selected at a time).

Classes:
    SingleSelectionState: Single selection state - immutable.
"""

from __future__ import annotations

from promptosaurus.ui.state.selection_state import SelectionState


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

    def navigate_with_columns(self, direction: int, items_per_column: int) -> SingleSelectionState:
        """Return new state after navigation in multi-column layout.

        In a multi-column layout, UP/DOWN should navigate within the same
        column (jumping by items_per_column), not just by 1.

        Example with 4 columns and items_per_column=6:
            Position:  0  1  2  3
                       4  5  6  7
                       8  9 10 11
                      12 13 14 15

        If selected is 5 and user presses DOWN, goes to 9 (same column, next row).
        If selected is 9 and user presses UP, goes to 5 (same column, previous row).

        Args:
            direction: Navigation direction (-1 for up, +1 for down).
            items_per_column: Number of items per column.

        Returns:
            New SingleSelectionState after column-aware navigation.
        """
        # Calculate navigation distance based on column layout
        navigation_distance = direction * items_per_column
        new_index = max(0, min(self._max, self._selected + navigation_distance))
        return SingleSelectionState(new_index, self._max)

    def is_selected(self, index: int) -> bool:
        """Check if index is selected.

        Args:
            index: The index to check.

        Returns:
            True if the index is currently selected.
        """
        return index == self._selected
