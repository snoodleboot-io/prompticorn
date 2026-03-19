import unittest
from promptosaurus.builders.template_handlers.linter_handler import LinterHandler


class TestLinterHandler(unittest.TestCase):
    """Test cases for the LinterHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = LinterHandler()

    def test_can_handle_linter(self):
        """Test that can_handle returns True for LINTER."""
        self.assertTrue(self.handler.can_handle("LINTER"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("FORMATTER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the linter value when present."""
        config = {"linter": "ruff"}
        result = self.handler.handle("LINTER", config)
        self.assertEqual(result, "ruff")

    def test_handle_without_value(self):
        """Test that handle returns empty string when linter is not present."""
        config = {}
        result = self.handler.handle("LINTER", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when linter is None."""
        config = {"linter": None}
        result = self.handler.handle("LINTER", config)
        self.assertEqual(result, "None")


if __name__ == '__main__':
    unittest.main()