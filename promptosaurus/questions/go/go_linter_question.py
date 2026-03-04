# Go linter question

from promptosaurus.questions.base.question import Question


class GoLinterQuestion(Question):
    """Question for Go linter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "go_linter"

    @property
    def question_text(self) -> str:
        return "What linter do you want to use for Go?"

    @property
    def explanation(self) -> str:
        return """Linters check code quality, style, and potential bugs. You can select multiple:
- golangci-lint: Fast, configurable, runs many linters in parallel
- golint: Official Google linter, focuses on style and conventions
- staticcheck: Advanced static analysis, finds bugs and performance issues"""

    @property
    def options(self) -> list[str]:
        return ["golangci-lint", "golint", "staticcheck"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "golangci-lint": "Fast and configurable - runs 50+ linters in parallel, highly recommended",
            "golint": "Official Google style - focuses on naming and style conventions",
            "staticcheck": "Advanced analysis - finds bugs, performance issues, and deprecated APIs",
        }

    @property
    def default(self) -> str:
        return "golangci-lint"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple linters."""
        return True
