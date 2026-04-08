import unittest

from promptosaurus.builders.template_handlers.package_manager_handler import PackageManagerHandler


class TestPackageManagerHandler(unittest.TestCase):
    """Test cases for the PackageManagerHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = PackageManagerHandler()

    def test_can_handle_package_manager(self):
        """Test that can_handle returns True for PACKAGE_MANAGER."""
        self.assertTrue(self.handler.can_handle("PACKAGE_MANAGER"))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for other variable names."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("RUNTIME"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_value(self):
        """Test that handle returns the package_manager value when present."""
        config = {"package_manager": "uv"}
        result = self.handler.handle("PACKAGE_MANAGER", config)
        self.assertEqual(result, "uv")

    def test_handle_without_value(self):
        """Test that handle returns empty string when package_manager is not present."""
        config = {}
        result = self.handler.handle("PACKAGE_MANAGER", config)
        self.assertEqual(result, "")

    def test_handle_with_none_value(self):
        """Test that handle returns empty string when package_manager is None."""
        config = {"package_manager": None}
        result = self.handler.handle("PACKAGE_MANAGER", config)
        self.assertEqual(result, "None")


if __name__ == "__main__":
    unittest.main()
