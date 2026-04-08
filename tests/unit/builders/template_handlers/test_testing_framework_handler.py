import unittest

from promptosaurus.builders.template_handlers.testing_framework_handler import (
    TestingFrameworkHandler,
)


class TestTestingFrameworkHandler(unittest.TestCase):
    """Test cases for the TestingFrameworkHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = TestingFrameworkHandler()

    def test_can_handle_testing_framework(self):
        """Test that can_handle returns True for TESTING_FRAMEWORK."""
        self.assertTrue(self.handler.can_handle("TESTING_FRAMEWORK"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("TEST_RUNNER"))
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the test_framework value when present."""
        config = {"test_framework": "pytest"}
        result = self.handler.handle("TESTING_FRAMEWORK", config)
        self.assertEqual(result, "pytest")

    def test_handle_without_value(self):
        """Test that handle returns empty string when test_framework is not present."""
        config = {}
        result = self.handler.handle("TESTING_FRAMEWORK", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when test_framework is None."""
        config = {"test_framework": None}
        result = self.handler.handle("TESTING_FRAMEWORK", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
