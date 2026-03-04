# Shell linter question

from promptosaurus.questions.base.question import Question


class ShellLinterQuestion(Question):
    """Question handler for shell linter."""

    @property
    def key(self) -> str:
        return "shell_linter"

    @property
    def question_text(self) -> str:
        return "What linter do you want to use for shell scripts?"

    @property
    def explanation(self) -> str:
        return """Shell linters catch bugs and enforce best practices.

- ShellCheck is the industry standard for shell script analysis
- It catches common mistakes and security issues
- Highly recommended for all shell scripting"""

    @property
    def options(self) -> list[str]:
        return ["shellcheck"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "shellcheck": "Industry standard - comprehensive analysis, catches bugs",
        }

    @property
    def default(self) -> str:
        return "shellcheck"
