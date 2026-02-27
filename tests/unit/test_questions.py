"""Tests for prompt init questions."""

import pytest

from promptcli.questions.base import (
    RepositoryTypeQuestion,
    FolderMappingQuestion,
    REPO_TYPE_SINGLE,
    REPO_TYPE_MULTI_FOLDER,
    REPO_TYPE_MIXED,
)
from promptcli.questions.python.python_package_manager_question import PythonPackageManagerQuestion
from promptcli.questions.python.python_runtime_question import PythonRuntimeQuestion
from promptcli.questions.python.python_test_framework_question import PythonTestFrameworkQuestion

from promptcli.questions.typescript import (
    TypeScriptVersionQuestion,
    TypeScriptPackageManagerQuestion,
)
from promptcli.questions.language import (
    get_language_questions,
    LANGUAGE_KEYS,
)


class TestRepositoryTypeQuestion:
    """Tests for RepositoryTypeQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = RepositoryTypeQuestion()

        assert q.key == "repository_type"
        assert q.question_text
        assert q.explanation
        assert q.options
        assert q.default

    def test_options_are_valid(self):
        """Options should include all valid repo types."""
        q = RepositoryTypeQuestion()

        assert REPO_TYPE_SINGLE in q.options
        assert REPO_TYPE_MULTI_FOLDER in q.options
        assert REPO_TYPE_MIXED in q.options

    def test_default_is_single_language(self):
        """Default should be single-language."""
        q = RepositoryTypeQuestion()

        assert q.default == REPO_TYPE_SINGLE

    def test_option_explanations_exist(self):
        """Each option should have an explanation."""
        q = RepositoryTypeQuestion()

        for opt in q.options:
            assert opt in q.option_explanations
            assert q.option_explanations[opt]

    def test_explain_option_returns_explanation(self):
        """explain_option should return the explanation for an option."""
        q = RepositoryTypeQuestion()

        explanation = q.explain_option(REPO_TYPE_SINGLE)
        assert explanation == q.option_explanations[REPO_TYPE_SINGLE]

    def test_explain_option_unknown_returns_empty(self):
        """explain_option for unknown option should return empty string."""
        q = RepositoryTypeQuestion()

        assert q.explain_option("unknown") == ""


class TestFolderMappingQuestion:
    """Tests for FolderMappingQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = FolderMappingQuestion()

        assert q.key == "folder_mapping"
        assert q.question_text
        assert q.explanation

    def test_options_is_empty_list(self):
        """Options should be empty for dynamic folder mapping."""
        q = FolderMappingQuestion()

        assert q.options == []

    def test_default_is_empty_string(self):
        """Default should be empty string for folder mapping."""
        q = FolderMappingQuestion()

        assert q.default == ""


class TestPythonRuntimeQuestion:
    """Tests for PythonRuntimeQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonRuntimeQuestion()

        assert q.key == "python_runtime"
        assert q.question_text
        assert q.explanation
        assert q.options
        assert q.default

    def test_options_include_common_runtimes(self):
        """Options should include common Python runtimes."""
        q = PythonRuntimeQuestion()

        assert "3.12" in q.options
        assert "3.11" in q.options
        assert "pypy" in q.options

    def test_default_is_latest_stable(self):
        """Default should be latest stable version."""
        q = PythonRuntimeQuestion()

        assert q.default == "3.12"

    def test_option_explanations_for_all_options(self):
        """Each option should have an explanation."""
        q = PythonRuntimeQuestion()

        for opt in q.options:
            assert opt in q.option_explanations


class TestPythonPackageManagerQuestion:
    """Tests for PythonPackageManagerQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonPackageManagerQuestion()

        assert q.key == "python_package_manager"
        assert q.options

    def test_options_include_common_managers(self):
        """Options should include common Python package managers."""
        q = PythonPackageManagerQuestion()

        assert "poetry" in q.options
        assert "pip" in q.options
        assert "uv" in q.options

    def test_default_is_poetry(self):
        """Default should be poetry."""
        q = PythonPackageManagerQuestion()

        assert q.default == "poetry"


class TestPythonTestFrameworkQuestion:
    """Tests for PythonTestFrameworkQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonTestFrameworkQuestion()

        assert q.key == "python_test_framework"
        assert q.options

    def test_options_include_common_frameworks(self):
        """Options should include common Python test frameworks."""
        q = PythonTestFrameworkQuestion()

        assert "pytest" in q.options
        assert "unittest" in q.options

    def test_default_is_pytest(self):
        """Default should be pytest."""
        q = PythonTestFrameworkQuestion()

        assert q.default == "pytest"


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


class TestGetLanguageQuestions:
    """Tests for get_language_questions function."""

    def test_get_python_questions(self):
        """Should return questions for Python."""
        questions = get_language_questions("python")

        assert len(questions) > 0
        keys = [q.key for q in questions]
        assert "python_runtime" in keys
        assert "python_package_manager" in keys

    def test_get_typescript_questions(self):
        """Should return questions for TypeScript."""
        questions = get_language_questions("typescript")

        assert len(questions) > 0
        keys = [q.key for q in questions]
        assert "typescript_version" in keys

    def test_get_javascript_questions(self):
        """Should return questions for JavaScript (same as TypeScript)."""
        questions = get_language_questions("javascript")

        assert len(questions) > 0

    def test_get_unknown_language_returns_empty(self):
        """Unknown language should return empty list."""
        questions = get_language_questions("unknown_language")

        assert questions == []

    def test_language_keys_includes_common_languages(self):
        """LANGUAGE_KEYS should include common languages."""
        assert "python" in LANGUAGE_KEYS
        assert "typescript" in LANGUAGE_KEYS
        assert "javascript" in LANGUAGE_KEYS
        assert "go" in LANGUAGE_KEYS
        assert "rust" in LANGUAGE_KEYS
