"""Question for selecting Python test framework."""

from promptosaurus.questions.base.question import Question


class PythonTestFrameworkQuestion(Question):
    """Question handler for Python test framework selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_test_framework"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What test framework?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select your preferred testing framework for unit and integration tests."

    @property
    def options(self) -> list[str]:
        """Available test frameworks."""
        return ["pytest", "unittest", "nose2"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "hybrid"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "pytest": "Flexible, powerful fixtures, excellent plugins",
            "unittest": "Standard library, minimal setup",
            "nose2": "Test discovery, plugins, unittest compatible",
        }
