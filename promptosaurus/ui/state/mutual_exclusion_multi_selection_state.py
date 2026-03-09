"""Mutual exclusion multi-selection state implementation.

This is a variant of multi-select where selecting "none" clears all other
selections, and selecting any other option clears "none". This is useful
for questions like "Which mocking libraries do you want?" where "none"
means no mocking at all and is mutually exclusive with any library selection.
"""

from __future__ import annotations

from promptosaurus.ui.state.selection_state import SelectionState


class MutualExclusionMultiSelectionState(SelectionState):
    """Multi-selection state with mutual exclusion - allows selecting multiple options
    but "none" is mutually exclusive with all other options.

    Behavior:
    - Selecting "none" clears all other selections
    - Selecting any non-none option clears "none" if selected
    - Multiple non-none options can be selected together
    """

    def __init__(self, selected: set[int], max_index: int, none_index: int):
        """Initialize with selected indices, max index, and the index representing 'none'.

        Args:
            selected: Set of currently selected indices
            max_index: Maximum valid index
            none_index: The index that represents "none" (mutually exclusive)
        """
        self._selected = frozenset(selected)
        self._max = max_index
        self._none_index = none_index

    @property
    def current_selection(self) -> set[int]:
        """Get current selections."""
        return set(self._selected)

    @property
    def none_index(self) -> int:
        """Get the index representing 'none'."""
        return self._none_index

    def select(self, index: int) -> MutualExclusionMultiSelectionState:
        """Toggle selection at index with mutual exclusion logic.

        If index is none_index:
            - If none_index was selected, deselect it (toggle off)
            - If none_index was not selected, select only none, clear all others
        If index is NOT none_index:
            - If index was selected, deselect it
            - If index was not selected, add it and clear none_index if selected
        """
        if index > self._max:
            return self

        if index == self._none_index:
            # User selected 'none' - clear all other selections
            if index in self._selected:
                # Toggle off - return empty selection
                return MutualExclusionMultiSelectionState(set(), self._max, self._none_index)
            else:
                # Toggle on - select only none, clear all others
                return MutualExclusionMultiSelectionState({index}, self._max, self._none_index)
        else:
            # User selected a non-none option
            if index in self._selected:
                # Remove this selection
                new_selected = set(self._selected)
                new_selected.remove(index)
                return MutualExclusionMultiSelectionState(new_selected, self._max, self._none_index)
            else:
                # Add this selection, but if none is selected, clear it
                new_selected = set(self._selected)
                # Clear none if it's selected
                if self._none_index in new_selected:
                    new_selected.remove(self._none_index)
                new_selected.add(index)
                return MutualExclusionMultiSelectionState(new_selected, self._max, self._none_index)

    def navigate(self, direction: int) -> MutualExclusionMultiSelectionState:
        """Multi-select doesn't use navigation - returns self."""
        return self

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        return index in self._selected
