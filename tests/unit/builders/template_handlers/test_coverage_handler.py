import unittest

from prompticorn.builders.template_handlers.coverage_handler import CoverageHandler


class TestCoverageHandler(unittest.TestCase):
    """Test cases for the CoverageHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = CoverageHandler()

    def test_can_handle_coverage_variables(self):
        """Test that can_handle returns True for all coverage variables."""
        coverage_vars = [
            "LINE_COVERAGE_%",
            "BRANCH_COVERAGE_%",
            "FUNCTION_COVERAGE_%",
            "STATEMENT_COVERAGE_%",
            "MUTATION_COVERAGE_%",
            "PATH_COVERAGE_%",
        ]
        for var in coverage_vars:
            with self.subTest(variable=var):
                self.assertTrue(self.handler.can_handle(var))

    def test_can_handle_other_variables(self):
        """Test that can_handle returns False for non-coverage variables."""
        self.assertFalse(self.handler.can_handle("LANGUAGE"))
        self.assertFalse(self.handler.can_handle("FORMATTER"))
        self.assertFalse(self.handler.can_handle(""))

    def test_handle_with_dict_coverage(self):
        """Test handle with coverage as dict."""
        config = {
            "coverage": {
                "line": 85,
                "branch": 75,
                "function": 92,
                "statement": 88,
                "mutation": 82,
                "path": 65,
            }
        }
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "85")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "75")
        self.assertEqual(self.handler.handle("FUNCTION_COVERAGE_%", config), "92")
        self.assertEqual(self.handler.handle("STATEMENT_COVERAGE_%", config), "88")
        self.assertEqual(self.handler.handle("MUTATION_COVERAGE_%", config), "82")
        self.assertEqual(self.handler.handle("PATH_COVERAGE_%", config), "65")

    def test_handle_with_string_coverage_strict(self):
        """Test handle with coverage as 'strict' preset."""
        config = {"coverage": "strict"}
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "90")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("FUNCTION_COVERAGE_%", config), "95")
        self.assertEqual(self.handler.handle("STATEMENT_COVERAGE_%", config), "90")
        self.assertEqual(self.handler.handle("MUTATION_COVERAGE_%", config), "85")
        self.assertEqual(self.handler.handle("PATH_COVERAGE_%", config), "70")

    def test_handle_with_string_coverage_standard(self):
        """Test handle with coverage as 'standard' preset."""
        config = {"coverage": "standard"}
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "70")
        self.assertEqual(self.handler.handle("FUNCTION_COVERAGE_%", config), "90")
        self.assertEqual(self.handler.handle("STATEMENT_COVERAGE_%", config), "85")
        self.assertEqual(self.handler.handle("MUTATION_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("PATH_COVERAGE_%", config), "60")

    def test_handle_with_string_coverage_minimal(self):
        """Test handle with coverage as 'minimal' preset."""
        config = {"coverage": "minimal"}
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "70")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "60")
        self.assertEqual(self.handler.handle("FUNCTION_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("STATEMENT_COVERAGE_%", config), "75")
        self.assertEqual(self.handler.handle("MUTATION_COVERAGE_%", config), "70")
        self.assertEqual(self.handler.handle("PATH_COVERAGE_%", config), "50")

    def test_handle_with_unknown_preset(self):
        """Test handle with unknown preset falls back to defaults."""
        config = {"coverage": "unknown"}
        # Should return default values
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "70")

    def test_handle_without_coverage_config(self):
        """Test handle when coverage config is missing."""
        config = {}
        # Should return default values
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "80")
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "70")

    def test_handle_with_partial_dict_coverage(self):
        """Test handle with partial coverage dict."""
        config = {"coverage": {"line": 90}}  # Only line specified
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "90")
        # Others should fall back to defaults
        self.assertEqual(self.handler.handle("BRANCH_COVERAGE_%", config), "70")

    def test_handle_with_invalid_coverage_type(self):
        """Test handle with invalid coverage type."""
        config = {"coverage": 123}  # Invalid type
        # Should treat as empty dict and return defaults
        self.assertEqual(self.handler.handle("LINE_COVERAGE_%", config), "80")


if __name__ == "__main__":
    unittest.main()
