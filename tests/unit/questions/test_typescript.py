"""Tests for TypeScript-specific questions."""

from prompticorn.questions.typescript.typescript_package_manager_question import (
    TypeScriptPackageManagerQuestion,
)
from prompticorn.questions.typescript.typescript_version_question import TypeScriptVersionQuestion


class TestTypeScriptVersionQuestion:
    """Tests for TypeScriptVersionQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = TypeScriptVersionQuestion()

        assert q.key == "typescript_version"
        assert q.options

    def test_options_include_recent_versions(self):
        """Options should include recent TypeScript versions with v prefix."""
        q = TypeScriptVersionQuestion()

        # Should have versions with 'v' prefix for clarity
        assert "v6.0" in q.options
        assert "v5.9" in q.options
        assert "v5.8" in q.options
        assert "v5.4" in q.options
        assert "v5.0" in q.options
        # Should NOT have placeholder versions or unprefixed versions
        assert "5.x" not in q.options
        assert "6.0" not in q.options  # Should be v6.0

    def test_default_is_latest(self):
        """Default should be latest stable version."""
        q = TypeScriptVersionQuestion()

        assert q.default == "v6.0"


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
