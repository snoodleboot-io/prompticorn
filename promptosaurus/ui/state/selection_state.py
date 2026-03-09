"""Base selection state implementation."""

from __future__ import annotations


class SelectionState:
    """Base class for selection state - Strategy pattern.

    Subclasses must override all methods.
    """

    @property
    def current_selection(self) -> int | set[int]:
        """Get current selection(s)."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement current_selection")

    def select(self, index: int) -> SelectionState:
        """Return new state after selection - immutable."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement select")

    def navigate(self, direction: int) -> SelectionState:
        """Return new state after navigation."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement navigate")

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement is_selected")
