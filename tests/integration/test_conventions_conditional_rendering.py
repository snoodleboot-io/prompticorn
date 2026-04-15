"""Integration tests for Jinja2 conditional rendering in conventions files."""

import sys
import unittest
from pathlib import Path

# Add promptosaurus to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer import (
    Jinja2TemplateRenderer,
)


class TestConventionsConditionalRendering(unittest.TestCase):
    """Test that conventions files render correctly with Jinja2 conditionals."""

    def setUp(self):
        """Set up test fixtures."""
        import jinja2

        # Set up Jinja2 environment with FileSystemLoader to resolve template imports
        core_dir = Path(__file__).parent.parent.parent / "promptosaurus" / "agents" / "core"
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(core_dir)),
            undefined=jinja2.StrictUndefined,
        )
        self.renderer = Jinja2TemplateRenderer(jinja_env)

        # Load the source conventions file directly (not the built version)
        # This allows us to test template rendering without needing the build step
        conventions_path = core_dir / "conventions-python.md"
        with open(conventions_path) as f:
            self.conventions_content = f.read()

        # Base variables required by the template (matching CoreFilesLoader._template_content)
        self.base_variables = {
            "language": "python",
            "runtime": "3.11",
            "package_manager": "poetry",
            "test_framework": "pytest",
            "linter": "ruff",
            "formatter": "ruff",
            "coverage_tool": "pytest-cov",
            "coverage_targets": {},
        }

    def test_interface_pattern_rendering(self):
        """Test that interface pattern renders when abstract_class_style == 'interface'."""
        variables = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        result = self.renderer.handle(self.conventions_content, variables)

        # Should contain interface pattern (traditional OOP interfaces)
        self.assertIn("#### Using Interface Pattern (Traditional OOP Interfaces)", result)
        self.assertIn("Interfaces are base classes with standard `__init__`", result)
        self.assertIn("raise NotImplementedError", result)
        self.assertIn("class Repository:", result)  # Base class without ABC/Protocol

        # Should NOT contain abc pattern
        self.assertNotIn("#### Using ABC Pattern (Abstract Base Classes)", result)
        self.assertNotIn("from abc import ABC, abstractmethod", result)
        self.assertNotIn("class Repository(ABC):", result)

    def test_abc_pattern_rendering(self):
        """Test that abc pattern renders when abstract_class_style == 'abc'."""
        variables = {
            **self.base_variables,
            "abstract_class_style": "abc",
            "config": {"abstract_class_style": "abc"},
        }
        result = self.renderer.handle(self.conventions_content, variables)

        # Should NOT contain interface pattern
        self.assertNotIn("#### Using Interface Pattern (Traditional OOP Interfaces)", result)
        self.assertNotIn("Interfaces are base classes with standard `__init__`", result)

        # Should contain abc pattern
        self.assertIn("#### Using Abstract Base Classes (abc module)", result)
        self.assertIn("from abc import ABC, abstractmethod", result)
        self.assertIn("class Repository(ABC):", result)

    def test_not_implemented_error_always_present(self):
        """Test that NotImplementedError pattern is present in interface style."""
        # The interface pattern uses NotImplementedError
        variables = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        result = self.renderer.handle(self.conventions_content, variables)

        # Interface pattern should contain NotImplementedError
        self.assertIn("raise NotImplementedError", result)

    def test_template_variable_substitution_interface(self):
        """Test that the template variable placeholder gets substituted for interface."""
        variables = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        result = self.renderer.handle(self.conventions_content, variables)

        # Should substitute template variable
        self.assertNotIn("[Template variable]", result)
        self.assertIn("Selected Style: **interface**", result)

    def test_template_variable_substitution_abc(self):
        """Test that the template variable placeholder gets substituted for abc."""
        variables = {
            **self.base_variables,
            "abstract_class_style": "abc",
            "config": {"abstract_class_style": "abc"},
        }
        result = self.renderer.handle(self.conventions_content, variables)

        # Should substitute template variable
        self.assertNotIn("[Template variable]", result)
        self.assertIn("Selected Style: **abc**", result)

    def test_conditional_sections_are_exclusive(self):
        """Test that interface and abc sections are mutually exclusive."""
        interface_vars = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        abc_vars = {
            **self.base_variables,
            "abstract_class_style": "abc",
            "config": {"abstract_class_style": "abc"},
        }

        interface_result = self.renderer.handle(self.conventions_content, interface_vars)
        abc_result = self.renderer.handle(self.conventions_content, abc_vars)

        # Interface result should have interface content but not abc content
        self.assertIn("Traditional OOP Interfaces", interface_result)
        self.assertNotIn("Abstract Base Classes", interface_result)

        # ABC result should have abc content but not interface content
        self.assertNotIn("Traditional OOP Interfaces", abc_result)
        self.assertIn("Abstract Base Classes", abc_result)

    def test_section_headers_render_correctly(self):
        """Test that section headers render correctly for each style."""
        # Test interface
        interface_vars = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        interface_result = self.renderer.handle(self.conventions_content, interface_vars)

        # Should have interface section header
        self.assertIn("#### Using Interface Pattern (Traditional OOP Interfaces)", interface_result)
        # Should not have abc section header
        self.assertNotIn("#### Using ABC Pattern (Abstract Base Classes)", interface_result)

        # Test abc
        abc_vars = {
            **self.base_variables,
            "abstract_class_style": "abc",
            "config": {"abstract_class_style": "abc"},
        }
        abc_result = self.renderer.handle(self.conventions_content, abc_vars)

        # Should have abc section header
        self.assertIn("#### Using Abstract Base Classes (abc module)", abc_result)
        # Should not have interface section header
        self.assertNotIn("#### Using Interface Pattern (Traditional OOP Interfaces)", abc_result)

    def test_code_examples_render_correctly(self):
        """Test that code examples render correctly for each style."""
        # Test interface examples
        interface_vars = {
            **self.base_variables,
            "abstract_class_style": "interface",
            "config": {"abstract_class_style": "interface"},
        }
        interface_result = self.renderer.handle(self.conventions_content, interface_vars)

        # Should contain interface-specific code patterns
        self.assertIn(
            "def __init__(self, connection_string: str, timeout: int = 30):", interface_result
        )
        self.assertIn("super().__init__(connection_string, timeout)", interface_result)
        self.assertIn(
            'raise NotImplementedError(f"{self.__class__.__name__} must implement', interface_result
        )

        # Should not contain abc-specific code
        self.assertNotIn("from abc import ABC, abstractmethod", interface_result)
        self.assertNotIn("class Repository(ABC):", interface_result)
        self.assertNotIn("@abstractmethod", interface_result)

        # Test abc examples
        abc_vars = {
            **self.base_variables,
            "abstract_class_style": "abc",
            "config": {"abstract_class_style": "abc"},
        }
        abc_result = self.renderer.handle(self.conventions_content, abc_vars)

        # Should contain abc-specific code
        self.assertIn("from abc import ABC, abstractmethod", abc_result)
        self.assertIn("class Repository(ABC):", abc_result)
        self.assertIn("@abstractmethod", abc_result)

        # Should not contain interface-specific patterns
        self.assertNotIn(
            "def __init__(self, connection_string: str, timeout: int = 30):", abc_result
        )
        self.assertNotIn("super().__init__(connection_string, timeout)", abc_result)


if __name__ == "__main__":
    unittest.main()
