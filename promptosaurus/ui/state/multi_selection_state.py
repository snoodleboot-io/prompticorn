"""Multi-selection state implementation."""

from __future__ import annotations

from promptosaurus.ui.state.selection_state import SelectionState


class MultiSelectionState(SelectionState):
    """Multi-selection state - allows selecting multiple options.

    This is the standard multi-select behavior where users can freely
    select or deselect any number of options without mutual exclusion.
    """

    def __init__(self, selected: set[int], max_index: int):
        self._selected = frozenset(selected)
        self._max = max_index

    @property
    def current_selection(self) -> set[int]:
        """Get current selections."""
        return set(self._selected)

    def select(self, index: int) -> MultiSelectionState:
        """Toggle selection at index."""
        if index > self._max:
            return self

        new_selected = set(self._selected)
        if index in new_selected:
            new_selected.remove(index)
        else:
            new_selected.add(index)
        return MultiSelectionState(new_selected, self._max)

    def navigate(self, direction: int) -> MultiSelectionState:
        """Multi-select doesn't use navigation - returns self."""
        return self

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        return index in self._selected
