# Rust formatter question

from promptcli.questions.base.question import Question


class RustFormatterQuestion(Question):
    """Question for Rust formatter."""

    @property
    def key(self) -> str:
        return "rust_formatter"

    @property
    def question_text(self) -> str:
        return "What formatter do you want to use for Rust?"

    @property
    def explanation(self) -> str:
        return """Formatters ensure consistent code style across your codebase.

- rustfmt is the official Rust formatter
- It automatically reformats code to follow Rust style guidelines
- Can be configured via rustfmt.toml for project-specific preferences
- Integrated with Cargo via `cargo fmt`"""

    @property
    def options(self) -> list[str]:
        return ["rustfmt"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "rustfmt": "Official formatter - enforces consistent style, configurable via rustfmt.toml",
        }

    @property
    def default(self) -> str:
        return "rustfmt"
