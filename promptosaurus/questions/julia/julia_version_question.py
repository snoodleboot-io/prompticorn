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

    @property
    def options(self) -> list[str]:
        return ["1.10", "1.9", "1.8"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.10": "Latest stable - best performance, recommended for new projects",
            "1.9": "Recent stable - excellent all-around",
            "1.8": "Long-term support - maximum package compatibility",
        }

    @property
    def default(self) -> str:
        return "1.10"
