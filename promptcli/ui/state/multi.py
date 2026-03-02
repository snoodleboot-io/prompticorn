"""Multi-selection state implementation."""

from promptcli.ui.state.selection_state import SelectionState


class MultiSelectState(SelectionState):
    """Multi-selection state - immutable."""

    def __init__(self, selected: set[int], max_index: int):
        self._selected = frozenset(selected)
        self._max = max_index

    @property
    def current_selection(self) -> set[int]:
        """Get current selections."""
        return set(self._selected)

    def select(self, index: int) -> "MultiSelectState":
        """Toggle selection at index."""
        if index > self._max:
            return self
        new_selected = set(self._selected)
        if index in new_selected:
            new_selected.remove(index)
        else:
            new_selected.add(index)
        return MultiSelectState(new_selected, self._max)

    def navigate(self, direction: int) -> "MultiSelectState":
        """Multi-select doesn't use navigation - returns self."""
        return self

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        return index in self._selected
