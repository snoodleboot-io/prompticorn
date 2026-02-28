# Rust version question

from promptcli.questions.base.question import Question


class RustVersionQuestion(Question):
    """Question for Rust version selection."""

    @property
    def key(self) -> str:
        return "rust_version"

    @property
    def question_text(self) -> str:
        return "What Rust version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Rust version affects language features, performance, and crate compatibility.

- Newer versions have better performance and compiler improvements
- Edition 2021 is the current standard (enabled by default in 1.56+)
- Async/await has been stable since 1.39
- Const generics have improved significantly in recent versions"""

    @property
    def options(self) -> list[str]:
        return ["1.75", "1.74", "1.73", "1.72"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.75": "Latest stable - const trait implementations, pointer byte offsets",
            "1.74": "Very stable - lint configuration through Cargo.toml, improved async fn",
            "1.73": "Stable - cleaner panic messages, new APIs in std",
            "1.72": "Mature - stable const traits in limited form, good compatibility",
        }

    @property
    def default(self) -> str:
        return "1.75"
