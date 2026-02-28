# Go formatter question

from promptcli.questions.base.question import Question


class GoFormatterQuestion(Question):
    """Question for Go formatter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "go_formatter"

    @property
    def question_text(self) -> str:
        return "What formatter do you want to use for Go?"

    @property
    def explanation(self) -> str:
        return """Formatters ensure consistent code style. You can select multiple:
- gofmt: Official Go formatter, standard style, included with Go
- gofumpt: Stricter version of gofmt, more opinionated formatting
- goimports: Formats and automatically manages import statements"""

    @property
    def options(self) -> list[str]:
        return ["gofmt", "gofumpt", "goimports"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "gofmt": "Official formatter - standard Go style, included with Go toolchain",
            "gofumpt": "Stricter gofmt - more opinionated, removes unnecessary blank lines",
            "goimports": "Import management - formats code and auto-adds/removes imports",
        }

    @property
    def default(self) -> str:
        return "gofmt"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple formatters."""
        return True
