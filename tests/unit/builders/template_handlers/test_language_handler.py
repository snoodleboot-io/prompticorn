import unittest

from promptosaurus.builders.template_handlers.language_handler import LanguageHandler


class TestLanguageHandler(unittest.TestCase):
    """Test cases for the LanguageHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = LanguageHandler()

    def test_can_handle_language(self):
        """Test that can_handle returns True for LANGUAGE."""
        self.assertTrue(self.handler.can_handle("LANGUAGE"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("FORMATTER"))
        self.assertFalse(self.handler.can_handle("LINTER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the language value when present."""
        config = {"language": "python"}
        result = self.handler.handle("LANGUAGE", config)
        self.assertEqual(result, "python")

    def test_handle_without_value(self):
        """Test that handle returns empty string when language is not present."""
        config = {}
        result = self.handler.handle("LANGUAGE", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when language is None."""
        config = {"language": None}
        result = self.handler.handle("LANGUAGE", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
