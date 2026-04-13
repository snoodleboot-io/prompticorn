"""Test that empty default_indices doesn't select first option."""

from promptosaurus.ui.state.multi_selection_state import MultiSelectionState


class TestEmptyDefaultIndices:
    """Test the fix for empty default_indices falsy bug."""
    
    def test_empty_set_is_falsy_but_should_work(self):
        """Demonstrates the bug: empty set() is falsy in Python."""
        # This is the bug - empty set is falsy
        empty_set = set()
        assert not empty_set, "Empty set is falsy in Python"
        
        # OLD BUGGY CODE: empty_set or {0} would return {0}
        buggy_result = empty_set or {0}
        assert buggy_result == {0}, "Buggy code selects index 0"
        
        # FIXED CODE: empty_set if empty_set is not None else {0}
        fixed_result = empty_set if empty_set is not None else {0}
        assert fixed_result == set(), "Fixed code preserves empty set"
    
    def test_multi_selection_state_empty_set(self):
        """MultiSelectionState should work with empty set."""
        # Arrange - empty set means no selections
        state = MultiSelectionState(set(), max_index=5)
        
        # Assert - should have no selections
        assert state.current_selection == set(), \
            f"Expected no selections, got {state.current_selection}"
    
    def test_multi_selection_state_populated_set(self):
        """MultiSelectionState should work with populated set."""
        # Arrange - set with indices means those are selected
        state = MultiSelectionState({1, 3}, max_index=5)
        
        # Assert
        assert state.current_selection == {1, 3}, \
            f"Expected {{1, 3}}, got {state.current_selection}"
