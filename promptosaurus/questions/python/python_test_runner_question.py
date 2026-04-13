"""Question for selecting Python test runner."""

from promptosaurus.questions.base.question import Question


class PythonTestRunnerQuestion(Question):
    """Question handler for Python test runner selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_test_runner"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What test runner?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select your preferred test runner for executing tests."

    @property
    def options(self) -> list[str]:
        """Available test runners."""
        return ["pytest", "nose2", "unittest"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "pytest"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "pytest": "Powerful, plugin ecosystem, excellent output",
            "nose2": "Automatic discovery, plugin support",
            "unittest": "Standard library, simple, built-in",
        }
