import unittest

from promptosaurus.builders.template_handlers.abstract_class_style_handler import (
    AbstractClassStyleHandler,
)


class TestAbstractClassStyleHandler(unittest.TestCase):
    """Test cases for the AbstractClassStyleHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = AbstractClassStyleHandler()

    def test_can_handle_abstract_class_style(self):
        """Test that can_handle returns True for ABSTRACT_CLASS_STYLE."""
        self.assertTrue(self.handler.can_handle("ABSTRACT_CLASS_STYLE"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("FORMATTER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the abstract_class_style value when present."""
        config = {"abstract_class_style": "interface"}
        result = self.handler.handle("ABSTRACT_CLASS_STYLE", config)
        self.assertEqual(result, "interface")

    def test_handle_without_value(self):
        """Test that handle returns empty string when abstract_class_style is not present."""
        config = {}
        result = self.handler.handle("ABSTRACT_CLASS_STYLE", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when abstract_class_style is None."""
        config = {"abstract_class_style": None}
        result = self.handler.handle("ABSTRACT_CLASS_STYLE", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
