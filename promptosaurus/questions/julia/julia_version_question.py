# Julia version question

from promptosaurus.questions.base.question import Question


class JuliaVersionQuestion(Question):
    """Question handler for Julia version."""

    @property
    def key(self) -> str:
        return "julia_version"

    @property
    def question_text(self) -> str:
        return "What Julia version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Julia version affects performance and language features.

- Newer versions have improved JIT compilation and optimizations
- Julia is designed for high-performance scientific computing
- Version affects package compatibility and language features"""
