# Java linter question

from promptcli.questions.base.question import Question


class JavaLinterQuestion(Question):
    """Question for Java linter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "java_linter"

    @property
    def question_text(self) -> str:
        return "What linter(s) do you want to use?"

    @property
    def explanation(self) -> str:
        return """Linters check code quality, style, and bugs. You can select multiple:
- checkstyle: Enforces coding standards and style conventions
- spotbugs: Static analysis for bug patterns (successor to FindBugs)
- pmd: Source code analyzer for bugs, dead code, and optimizations"""

    @property
    def options(self) -> list[str]:
        return ["checkstyle", "spotbugs", "pmd"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "checkstyle": "Style enforcer - ensures code follows style conventions, highly configurable",
            "spotbugs": "Bug finder - static analysis for bug patterns, successor to FindBugs",
            "pmd": "Code analyzer - finds bugs, dead code, suboptimal code, and style issues",
        }

    @property
    def default(self) -> str:
        return "checkstyle"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple linters."""
        return True
