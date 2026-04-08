# Rust version question

from promptosaurus.questions.base.question import Question


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
