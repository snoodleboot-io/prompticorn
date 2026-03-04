"""Single selection state implementation."""

from promptosaurus.ui.state.selection_state import SelectionState


class SingleSelectState(SelectionState):
    """Single selection state - immutable."""

    def __init__(self, selected: int, max_index: int):
        self._selected = selected
        self._max = max_index

    @property
    def current_selection(self) -> int:
        """Get current selection."""
        return self._selected

    def select(self, index: int) -> "SingleSelectState":
        """Return new state after selection."""
        if 0 <= index <= self._max:
            return SingleSelectState(index, self._max)
        return self

    def navigate(self, direction: int) -> "SingleSelectState":
        """Return new state after navigation."""
        new_index = max(0, min(self._max, self._selected + direction))
        return SingleSelectState(new_index, self._max)

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        return index == self._selected
