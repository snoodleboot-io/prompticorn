"""Unit tests for UI state classes."""

import unittest

from promptosaurus.ui.state.multi import MultiSelectState
from promptosaurus.ui.state.single_select_state import SingleSelectState


class TestSingleSelectState(unittest.TestCase):
    """Single selection state machine tests."""

    def test_initial_selection(self):
        """Test initial selection is set correctly."""
        state = SingleSelectState(0, 5)
        self.assertEqual(state.current_selection, 0)

    def test_select_valid_index(self):
        """Test selecting a valid index returns new state."""
        state = SingleSelectState(0, 5)
        new_state = state.select(3)
        self.assertEqual(new_state.current_selection, 3)
        self.assertEqual(state.current_selection, 0)  # Original unchanged

    def test_select_out_of_bounds_high(self):
        """Test selecting above max index returns unchanged state."""
        state = SingleSelectState(2, 5)
        new_state = state.select(10)
        self.assertEqual(new_state.current_selection, 2)  # Unchanged

    def test_select_out_of_bounds_low(self):
        """Test selecting below 0 returns unchanged state."""
        state = SingleSelectState(2, 5)
        new_state = state.select(-1)
        self.assertEqual(new_state.current_selection, 2)  # Unchanged

    def test_navigate_up(self):
        """Test navigating up decreases selection."""
        state = SingleSelectState(2, 5)
        new_state = state.navigate(-1)
        self.assertEqual(new_state.current_selection, 1)

    def test_navigate_up_at_boundary(self):
        """Test navigating up at boundary stays at 0."""
        state = SingleSelectState(0, 5)
        new_state = state.navigate(-1)
        self.assertEqual(new_state.current_selection, 0)  # Stays at boundary

    def test_navigate_down(self):
        """Test navigating down increases selection."""
        state = SingleSelectState(2, 5)
        new_state = state.navigate(1)
        self.assertEqual(new_state.current_selection, 3)

    def test_navigate_down_at_boundary(self):
        """Test navigating down at boundary stays at max."""
        state = SingleSelectState(4, 4)  # 5 options, max valid index is 4
        new_state = state.navigate(1)
        self.assertEqual(new_state.current_selection, 4)  # Stays at boundary

    def test_is_selected_true(self):
        """Test is_selected returns True for current selection."""
        state = SingleSelectState(2, 5)
        self.assertTrue(state.is_selected(2))

    def test_is_selected_false(self):
        """Test is_selected returns False for non-selection."""
        state = SingleSelectState(2, 5)
        self.assertFalse(state.is_selected(3))

    def test_immutability(self):
        """Test that original state is not modified."""
        state = SingleSelectState(0, 5)
        state.select(3)
        state.navigate(2)
        self.assertEqual(state.current_selection, 0)  # Original unchanged


class TestMultiSelectState(unittest.TestCase):
    """Multi-selection state machine tests."""

    def test_initial_selection(self):
        """Test initial selections are set correctly."""
        state = MultiSelectState({0, 2}, 5)
        self.assertEqual(state.current_selection, {0, 2})

    def test_toggle_add(self):
        """Test selecting unselected index adds it."""
        state = MultiSelectState({0}, 5)
        new_state = state.select(2)
        self.assertTrue(new_state.is_selected(0))
        self.assertTrue(new_state.is_selected(2))

    def test_toggle_remove(self):
        """Test selecting selected index removes it."""
        state = MultiSelectState({0, 2}, 5)
        new_state = state.select(2)
        self.assertTrue(new_state.is_selected(0))
        self.assertFalse(new_state.is_selected(2))

    def test_navigate_noop(self):
        """Test multi-select doesn't use navigation."""
        state = MultiSelectState({0}, 5)
        new_state = state.navigate(1)
        self.assertEqual(new_state.current_selection, {0})

    def test_select_out_of_bounds(self):
        """Test selecting above max returns unchanged state."""
        state = MultiSelectState({0}, 5)
        new_state = state.select(10)
        self.assertEqual(new_state.current_selection, {0})

    def test_is_selected_true(self):
        """Test is_selected returns True for selected index."""
        state = MultiSelectState({0, 2, 4}, 5)
        self.assertTrue(state.is_selected(2))

    def test_is_selected_false(self):
        """Test is_selected returns False for unselected index."""
        state = MultiSelectState({0, 2, 4}, 5)
        self.assertFalse(state.is_selected(1))

    def test_empty_selection(self):
        """Test empty selection set."""
        state = MultiSelectState(set(), 5)
        self.assertEqual(state.current_selection, set())
        self.assertFalse(state.is_selected(0))

    def test_select_all(self):
        """Test selecting all options."""
        state = MultiSelectState(set(), 3)
        state = state.select(0)
        state = state.select(1)
        state = state.select(2)
        self.assertEqual(state.current_selection, {0, 1, 2})

    def test_immutability(self):
        """Test that original state is not modified."""
        state = MultiSelectState({0}, 5)
        state.select(2)
        state.select(0)  # Toggle off
        self.assertEqual(state.current_selection, {0})  # Original unchanged


if __name__ == "__main__":
    unittest.main()
