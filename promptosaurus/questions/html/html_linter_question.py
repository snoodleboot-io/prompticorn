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
        return ["htmlhint", "W3C Validator", "ESLint (with html plugin)", "none"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "htmlhint": "Fast, configurable, good IDE integration",
            "W3C Validator": "Official spec compliance checker",
            "ESLint (with html plugin)": "Best if using JavaScript heavily in HTML",
            "none": "No linter - manual validation only",
        }

    @property
    def default(self) -> str:
        return "htmlhint"
