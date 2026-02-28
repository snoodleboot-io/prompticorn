"""Single selection state implementation."""


class SelectionState:
    """Base class for selection state - Strategy pattern.

    Subclasses must override all methods.
    """

    @property
    def current_selection(self) -> int | set[int]:
        """Get current selection(s)."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement current_selection")

    def select(self, index: int) -> "SelectionState":
        """Return new state after selection - immutable."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement select")

    def navigate(self, direction: int) -> "SelectionState":
        """Return new state after navigation."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement navigate")

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement is_selected")


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
