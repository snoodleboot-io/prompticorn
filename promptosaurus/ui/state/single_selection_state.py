"""Single selection state implementation.

This module provides the SingleSelectionState class for managing
single-option selection behavior (only one option can be selected at a time).

Classes:
    SingleSelectionState: Single selection state - immutable.

Example:
    >>> from promptosaurus.ui.state.single_selection_state import SingleSelectionState
    >>>
    >>> state = SingleSelectionState(selected=0, max_index=3)
    >>> print(state.current_selection)
    0
    >>>
    >>> # Navigate
    >>> new_state = state.navigate(1)
    >>> print(new_state.current_selection)
    1
    >>>
    >>> # Select
    >>> new_state = state.select(2)
    >>> print(new_state.current_selection)
    2
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

    Example:
        >>> state = SingleSelectionState(selected=1, max_index=4)
        >>> state.is_selected(1)
        True
        >>> state.is_selected(2)
        False
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

        Example:
            >>> state = SingleSelectionState(selected=2, max_index=5)
            >>> state.current_selection
            2
        """
        return self._selected

    def select(self, index: int) -> SingleSelectionState:
        """Return new state after selection.

        Sets the selection to the specified index if valid.

        Args:
            index: The index to select.

        Returns:
            New SingleSelectionState with the selection applied.

        Example:
            >>> state = SingleSelectionState(selected=0, max_index=3)
            >>> new_state = state.select(2)
            >>> new_state.current_selection
            2
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

        Example:
            >>> state = SingleSelectionState(selected=1, max_index=3)
            >>> new_state = state.navigate(1)  # Move down
            >>> new_state.current_selection
            2
        """
        new_index = max(0, min(self._max, self._selected + direction))
        return SingleSelectionState(new_index, self._max)

    def is_selected(self, index: int) -> bool:
        """Check if index is selected.

        Args:
            index: The index to check.

        Returns:
            True if the index is currently selected.

        Example:
            >>> state = SingleSelectionState(selected=1, max_index=3)
            >>> state.is_selected(1)
            True
            >>> state.is_selected(2)
            False
        """
        return index == self._selected
