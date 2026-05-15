import unittest

from prompticorn.builders.template_handlers.formatter_handler import FormatterHandler


class TestFormatterHandler(unittest.TestCase):
    """Test cases for the FormatterHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = FormatterHandler()

    def test_can_handle_formatter(self):
        """Test that can_handle returns True for FORMATTER."""
        self.assertTrue(self.handler.can_handle("FORMATTER"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("LINTER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the formatter value when present."""
        config = {"formatter": "ruff"}
        result = self.handler.handle("FORMATTER", config)
        self.assertEqual(result, "ruff")

    def test_handle_without_value(self):
        """Test that handle returns empty string when formatter is not present."""
        config = {}
        result = self.handler.handle("FORMATTER", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when formatter is None."""
        config = {"formatter": None}
        result = self.handler.handle("FORMATTER", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
