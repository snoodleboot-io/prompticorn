"""Tests for TypeScript-specific questions."""

import pytest

from promptosaurus.questions.typescript.typescript_framework_question import (
    TypeScriptFrameworkQuestion,
)
from promptosaurus.questions.typescript.typescript_version_question import TypeScriptVersionQuestion
from promptosaurus.questions.typescript.typescript_package_manager_question import TypeScriptPackageManagerQuestion


class TestTypeScriptVersionQuestion:
    """Tests for TypeScriptVersionQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = TypeScriptVersionQuestion()

        assert q.key == "typescript_version"
        assert q.options

    def test_options_include_recent_versions(self):
        """Options should include recent TypeScript versions."""
        q = TypeScriptVersionQuestion()

        # Updated to match new real versions: 6.0, 5.9, 5.8, ..., 5.0
        assert "6.0" in q.options
        assert "5.9" in q.options
        assert "5.8" in q.options
        assert "5.4" in q.options
        assert "5.0" in q.options
        # Should NOT have placeholder versions
        assert "5.x" not in q.options
        assert "4.x" not in q.options

    def test_default_is_latest(self):
        """Default should be latest stable version."""
        q = TypeScriptVersionQuestion()

        assert q.default == "6.0"


class TestTypeScriptPackageManagerQuestion:
    """Tests for TypeScriptPackageManagerQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = TypeScriptPackageManagerQuestion()

        assert q.key == "typescript_package_manager"
        assert q.options

    def test_options_include_common_managers(self):
        """Options should include common package managers."""
        q = TypeScriptPackageManagerQuestion()

        # Updated to match new options: ["pnpm", "npm", "yarn"]
        assert "pnpm" in q.options
        assert "npm" in q.options
        assert "yarn" in q.options
