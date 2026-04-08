import unittest

from promptosaurus.builders.template_handlers.test_runner_handler import TestRunnerHandler


class TestTestRunnerHandler(unittest.TestCase):
    """Test cases for the TestRunnerHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = TestRunnerHandler()

    def test_can_handle_test_runner(self):
        """Test that can_handle returns True for TEST_RUNNER."""
        self.assertTrue(self.handler.can_handle("TEST_RUNNER"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("TESTING_FRAMEWORK"))
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the test_runner value when present."""
        config = {"test_runner": "pytest"}
        result = self.handler.handle("TEST_RUNNER", config)
        self.assertEqual(result, "pytest")

    def test_handle_without_value(self):
        """Test that handle returns empty string when test_runner is not present."""
        config = {}
        result = self.handler.handle("TEST_RUNNER", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when test_runner is None."""
        config = {"test_runner": None}
        result = self.handler.handle("TEST_RUNNER", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
