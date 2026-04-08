"""Base selection state implementation.

This module defines the base SelectionState class using the Strategy pattern.
Different selection behaviors (single, multi, mutual exclusion) are implemented
as separate subclasses.

Classes:
    SelectionState: Abstract base class for selection state - Strategy pattern.
"""

from __future__ import annotations


class SelectionState:
    """Base class for selection state - Strategy pattern.

    This abstract base class defines the interface for selection state
    management. The Strategy pattern allows different selection behaviors
    to be swapped at runtime.

    Subclasses must override all methods to provide concrete implementations
    for their specific selection behavior.

    Attributes:
        current_selection: Property returning current selection(s).

    Methods:
        select: Return new state after selection (immutable).
        navigate: Return new state after navigation.
        is_selected: Check if index is selected.
    """

    @property
    def current_selection(self) -> int | set[int]:
        """Get current selection(s).

        Returns:
            For single selection: the selected index as int.
            For multi selection: set of selected indices.

        Raises:
            NotImplementedError: If subclass doesn't implement this property.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement current_selection")

    def select(self, index: int) -> SelectionState:
        """Return new state after selection - immutable.

        Creates a new state instance with the selection applied.
        The original state remains unchanged (immutable pattern).

        Args:
            index: The index to select.

        Returns:
            New SelectionState with the selection applied.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement select")

    def navigate(self, direction: int) -> SelectionState:
        """Return new state after navigation.

        Args:
            direction: Navigation direction (-1 for up, +1 for down).

        Returns:
            New SelectionState after navigation.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement navigate")

    def is_selected(self, index: int) -> bool:
        """Check if index is selected.

        Args:
            index: The index to check.

        Returns:
            True if the index is currently selected.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement is_selected")
