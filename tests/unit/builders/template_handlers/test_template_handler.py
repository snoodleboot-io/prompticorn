import unittest
from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class TestTemplateHandler(unittest.TestCase):
    """Test cases for the TemplateHandler abstract base class."""

    def test_can_handle_raises_not_implemented(self):
        """Test that can_handle raises NotImplementedError."""
        handler = TemplateHandler()
        with self.assertRaises(NotImplementedError):
            handler.can_handle("test_variable")

    def test_handle_raises_not_implemented(self):
        """Test that handle raises NotImplementedError."""
        handler = TemplateHandler()
        with self.assertRaises(NotImplementedError):
            handler.handle("test_variable", {})


if __name__ == '__main__':
    unittest.main()