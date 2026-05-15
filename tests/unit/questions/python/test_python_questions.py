"""Tests for prompticorn.questions.python module."""

from prompticorn.questions.python.python_abstract_class_style_question import (
    PythonAbstractClassStyleQuestion,
)
from prompticorn.questions.python.python_formatter_question import PythonFormatterQuestion
from prompticorn.questions.python.python_linter_question import PythonLinterQuestion
from prompticorn.questions.python.python_package_manager_question import (
    PythonPackageManagerQuestion,
)
from prompticorn.questions.python.python_runtime_question import PythonRuntimeQuestion
from prompticorn.questions.python.python_test_framework_question import (
    PythonTestFrameworkQuestion,
)
from prompticorn.questions.python.python_test_runner_question import PythonTestRunnerQuestion


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

        assert q.default == "3.14"

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


class TestPythonAbstractClassStyleQuestion:
    """Tests for PythonAbstractClassStyleQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = PythonAbstractClassStyleQuestion()

        assert q.key == "python_abstract_class_style"
        assert q.question_text
        assert q.explanation
        assert q.options
        assert q.default

    def test_options_include_both_styles(self):
        """Options should include both abstract class styles."""
        q = PythonAbstractClassStyleQuestion()

        assert "abc" in q.options
        assert "interface" in q.options

    def test_default_is_interface(self):
        """Default should be interface."""
        q = PythonAbstractClassStyleQuestion()

        assert q.default == "interface"

    def test_option_explanations_for_all_options(self):
        """Each option should have an explanation."""
        q = PythonAbstractClassStyleQuestion()

        for opt in q.options:
            assert opt in q.option_explanations
