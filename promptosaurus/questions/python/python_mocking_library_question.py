# Python mocking library question

from promptosaurus.questions.base.question import Question


class PythonMockingLibraryQuestion(Question):
    """Question for Python mocking library selection (multi-select)."""

    @property
    def key(self) -> str:
        return "mocking_library"

    @property
    def question_text(self) -> str:
        return "What mocking libraries do you want to use?"

    @property
    def explanation(self) -> str:
        return """Select mocking libraries for your project. Choose multiple options or select 'none' for no mocking.
- unittest.mock: Built-in, no dependencies, standard library
- pytest-mock: pytest plugin wrapping unittest.mock with convenient fixtures
- freezegun: Mock time/date for testing time-dependent code
- responses: Mock HTTP requests/responses
- none: No mocking (use real objects for integration/acceptance tests)"""

    @property
    def options(self) -> list[str]:
        return ["unittest.mock", "pytest-mock", "freezegun", "responses", "none"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "unittest.mock": "Built-in - no dependencies, standard library, widely used",
            "pytest-mock": "pytest plugin - convenient fixture injection, cleaner syntax (recommended)",
            "freezegun": "Mock time/date - freeze datetime for testing time-dependent code",
            "responses": "Mock HTTP - mock requests library responses for API testing",
            "none": "No mocking - use real objects for integration/acceptance tests",
        }

    @property
    def allow_multiple(self) -> bool:
        return True

    @property
    def default(self) -> str:
        return "pytest-mock"

    @property
    def default_indices(self) -> set[int]:
        # Default to pytest-mock (index 1)
        return {1}

    @property
    def none_index(self) -> int | None:
        # 'none' is at index 4
        return 4
