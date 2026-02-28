# Rust linter question

from promptcli.questions.base.question import Question


class RustLinterQuestion(Question):
    """Question for Rust linter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "rust_linter"

    @property
    def question_text(self) -> str:
        return "What linter do you want to use for Rust?"

    @property
    def explanation(self) -> str:
        return """Linters check code quality, style, and potential bugs. You can select multiple:
- clippy: Official Rust linter with 500+ lints, catches common mistakes and style issues
- rustc: The Rust compiler's built-in warnings and lints, always enabled"""

    @property
    def options(self) -> list[str]:
        return ["clippy", "rustc"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "clippy": "Official linter - 500+ lints, catches common mistakes, highly recommended",
            "rustc": "Compiler lints - built-in warnings, always runs during compilation",
        }

    @property
    def default(self) -> str:
        return "clippy"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple linters."""
        return True
