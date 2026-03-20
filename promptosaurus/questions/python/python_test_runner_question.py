# Python test runner question

from promptosaurus.questions.base.question import Question


class PythonTestRunnerQuestion(Question):
    """Question for Python test runner (how tests are executed)."""

    @property
    def key(self) -> str:
        return "python_test_runner"

    @property
    def question_text(self) -> str:
        return "What test runner do you want to use?"

    @property
    def options(self) -> list[str]:
        return ["pytest", "nose2", "unittest"]

    @property
    def explanation(self) -> str:
        return """Test runner affects how tests are executed:
- pytest: Recommended, runs pytest/unittest/doctest/nose2
- nose2: Runs unittest and pytest-compatible tests
- unittest: Built-in test runner"""

    @property
    def default(self) -> str:
        return "pytest"

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "pytest": "Recommended, runs pytest/unittest/doctest/nose2",
            "nose2": "Runs unittest and pytest-compatible tests",
            "unittest": "Built-in test runner",
        }
