# HTML linter question

from promptosaurus.questions.base.question import Question


class HtmlLinterQuestion(Question):
    """Question handler for HTML linter choice."""

    @property
    def key(self) -> str:
        return "html_linter"

    @property
    def question_text(self) -> str:
        return "Which HTML linter do you want to use?"

    @property
    def explanation(self) -> str:
        return """HTML linters catch errors, accessibility issues, and best practice violations.

- htmlhint is fast and configurable
- W3C validator is the official spec checker
- ESLint with html plugin for JS-heavy projects"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["htmlhint", "W3C Validator", "ESLint (html plugin)"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "htmlhint"

    config_key = "linter"
