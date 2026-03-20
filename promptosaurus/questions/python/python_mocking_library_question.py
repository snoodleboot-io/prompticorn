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
    def default(self) -> str:
        return "unittest.mock"

    @property
    def allow_multiple(self) -> bool:
        return True
