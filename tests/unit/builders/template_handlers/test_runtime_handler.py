import unittest

from promptosaurus.builders.template_handlers.runtime_handler import RuntimeHandler


class TestRuntimeHandler(unittest.TestCase):
    """Test cases for the RuntimeHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = RuntimeHandler()

    def test_can_handle_runtime(self):
        """Test that can_handle returns True for RUNTIME."""
        self.assertTrue(self.handler.can_handle("RUNTIME"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("PACKAGE_MANAGER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the runtime value when present."""
        config = {"runtime": "3.12"}
        result = self.handler.handle("RUNTIME", config)
        self.assertEqual(result, "3.12")

    def test_handle_without_value(self):
        """Test that handle returns empty string when runtime is not present."""
        config = {}
        result = self.handler.handle("RUNTIME", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when runtime is None."""
        config = {"runtime": None}
        result = self.handler.handle("RUNTIME", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
