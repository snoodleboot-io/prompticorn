# Elm test framework question

from prompticorn.questions.base.question import Question


class ElmTestFrameworkQuestion(Question):
    """Question handler for Elm test framework."""

    @property
    def key(self) -> str:
        return "elm_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Elm?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure for testing Elm applications.

- elm-test is the standard testing framework for Elm
- It supports unit tests, fuzz tests (property-based testing)
- Integrates well with the Elm package ecosystem"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["elm-test", "elm-spec"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "elm-test"

    config_key = "test_framework"
