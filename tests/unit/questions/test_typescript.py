"""Tests for promptcli.questions.typescript module."""

import pytest

from promptcli.questions.typescript.typescript_version_question import (
    TypeScriptVersionQuestion,
)
from promptcli.questions.typescript.typescript_package_manager_question import (
    TypeScriptPackageManagerQuestion,
)


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

        assert "5.4" in q.options
        assert "5.3" in q.options
        assert "5.0" in q.options

    def test_default_is_latest(self):
        """Default should be latest stable version."""
        q = TypeScriptVersionQuestion()

        assert q.default == "5.4"


class TestTypeScriptPackageManagerQuestion:
    """Tests for TypeScriptPackageManagerQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = TypeScriptPackageManagerQuestion()

        assert q.key == "typescript_package_manager"
        assert q.options

    def test_options_include_common_managers(self):
        """Options should include common JS package managers."""
        q = TypeScriptPackageManagerQuestion()

        assert "npm" in q.options
        assert "pnpm" in q.options
        assert "yarn" in q.options
