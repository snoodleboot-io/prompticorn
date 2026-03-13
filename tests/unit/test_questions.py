"""Tests for prompt init questions."""

import pytest

from promptosaurus.questions.base.constants import (
    REPO_TYPE_MIXED,
    REPO_TYPE_MULTI_MONOREPO,
    REPO_TYPE_SINGLE,
)
from promptosaurus.questions.base.folder_mapping_question import FolderMappingQuestion
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion
from promptosaurus.questions.handlers.handle_single_language_questions import (
    HandleSingleLanguageQuestions,
)
from promptosaurus.questions.handlers.language_question_handler import LanguageQuestionHandler
from promptosaurus.questions.language import (
    LANGUAGE_KEYS,
    get_language_questions,
)
from promptosaurus.questions.python.python_formatter_question import PythonFormatterQuestion
from promptosaurus.questions.python.python_linter_question import PythonLinterQuestion
from promptosaurus.questions.python.python_package_manager_question import (
    PythonPackageManagerQuestion,
)
from promptosaurus.questions.python.python_runtime_question import PythonRuntimeQuestion
from promptosaurus.questions.python.python_test_framework_question import (
    PythonTestFrameworkQuestion,
)
from promptosaurus.questions.python.python_test_runner_question import PythonTestRunnerQuestion
from promptosaurus.questions.typescript.typescript_package_manager_question import (
    TypeScriptPackageManagerQuestion,
)
from promptosaurus.questions.typescript.typescript_version_question import (
    TypeScriptVersionQuestion,
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
        assert REPO_TYPE_MULTI_MONOREPO in q.options
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

    def test_default_is_uv(self):
        """Default should be uv."""
        q = PythonPackageManagerQuestion()

        assert q.default == "uv"


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

    def test_default_is_hybrid(self):
        """Default should be hybrid."""
        q = PythonTestFrameworkQuestion()

        assert q.default == "hybrid"


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
        """Unknown language should raise ValueError."""
        with pytest.raises(ValueError):
            get_language_questions("unknown_language")

    def test_language_keys_includes_common_languages(self):
        """LANGUAGE_KEYS should include common languages."""
        assert "python" in LANGUAGE_KEYS
        assert "typescript" in LANGUAGE_KEYS
        assert "javascript" in LANGUAGE_KEYS
        assert "go" in LANGUAGE_KEYS
        assert "rust" in LANGUAGE_KEYS


class TestPythonLinterQuestion:
    """Tests for PythonLinterQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonLinterQuestion()

        assert q.key == "python_linter"
        assert q.question_text
        assert q.explanation
        assert q.options

    def test_options_include_common_linters(self):
        """Options should include common Python linters."""
        q = PythonLinterQuestion()

        assert "ruff" in q.options
        assert "flake8" in q.options
        assert "pylint" in q.options
        assert "pyright" in q.options

    def test_default_is_ruff(self):
        """Default should be ruff."""
        q = PythonLinterQuestion()

        assert q.default == "ruff"

    def test_allow_multiple_is_true(self):
        """Should allow multiple selections."""
        q = PythonLinterQuestion()

        assert q.allow_multiple is True

    def test_option_explanations_for_all_options(self):
        """Each option should have an explanation."""
        q = PythonLinterQuestion()

        for opt in q.options:
            assert opt in q.option_explanations


class TestPythonFormatterQuestion:
    """Tests for PythonFormatterQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonFormatterQuestion()

        assert q.key == "python_formatter"
        assert q.question_text
        assert q.explanation
        assert q.options

    def test_options_include_common_formatters(self):
        """Options should include common Python formatters."""
        q = PythonFormatterQuestion()

        assert "ruff" in q.options
        assert "black" in q.options
        assert "yapf" in q.options

    def test_default_is_ruff(self):
        """Default should be ruff."""
        q = PythonFormatterQuestion()

        assert q.default == "ruff"

    def test_allow_multiple_is_true(self):
        """Should allow multiple selections."""
        q = PythonFormatterQuestion()

        assert q.allow_multiple is True

    def test_option_explanations_for_all_options(self):
        """Each option should have an explanation."""
        q = PythonFormatterQuestion()

        for opt in q.options:
            assert opt in q.option_explanations


class TestPythonTestRunnerQuestion:
    """Tests for PythonTestRunnerQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonTestRunnerQuestion()

        assert q.key == "python_test_runner"
        assert q.question_text
        assert q.explanation
        assert q.options

    def test_options_include_common_runners(self):
        """Options should include common test runners."""
        q = PythonTestRunnerQuestion()

        assert "pytest" in q.options
        assert "nose2" in q.options
        assert "unittest" in q.options

    def test_default_is_pytest(self):
        """Default should be pytest."""
        q = PythonTestRunnerQuestion()

        assert q.default == "pytest"

    def test_option_explanations_for_all_options(self):
        """Each option should have an explanation."""
        q = PythonTestRunnerQuestion()

        for opt in q.options:
            assert opt in q.option_explanations


class TestLanguageQuestionHandler:
    """Tests for LanguageQuestionHandler base class."""

    def test_handle_method_raises_not_implemented(self):
        """Base handle() method should raise NotImplementedError."""
        handler = LanguageQuestionHandler()

        with pytest.raises(NotImplementedError):
            handler.handle("single-language")


class TestHandleSingleLanguageQuestions:
    """Tests for HandleSingleLanguageQuestions handler."""

    def test_handler_initializes_with_selector(self):
        """Handler should initialize with a selector function."""

        def mock_selector(**kwargs):  # noqa: ARG001
            return "python"

        handler = HandleSingleLanguageQuestions(mock_selector)

        assert handler.select_option == mock_selector

    def test_handle_returns_config_dict(self, monkeypatch):
        """Handle should return a configuration dictionary."""

        def mock_selector(**kwargs):  # noqa: ARG001
            return "python"

        handler = HandleSingleLanguageQuestions(mock_selector)

        # Mock click.echo to avoid output during test
        monkeypatch.setattr("click.echo", lambda x: None)

        config = handler.handle("single-language")

        assert isinstance(config, dict)
        assert "spec" in config

    def test_python_questions_in_config(self, monkeypatch):
        """Python questions should populate config defaults."""

        def mock_selector(**kwargs):  # noqa: ARG001
            return "pytest" if "pytest" in kwargs.get("options", []) else "python"

        handler = HandleSingleLanguageQuestions(mock_selector)

        # Mock click.echo to avoid output during test
        monkeypatch.setattr("click.echo", lambda x: None)

        config = handler.handle("single-language")

        assert "spec" in config
        # Config should have some spec populated
        assert isinstance(config["spec"], dict)
