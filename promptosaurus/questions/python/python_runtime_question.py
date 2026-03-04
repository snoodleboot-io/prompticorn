# Python runtime question

from promptosaurus.questions.base.question import Question


class PythonRuntimeQuestion(Question):
    """Question handler for Python runtime/version."""

    @property
    def key(self) -> str:
        return "python_runtime"

    @property
    def question_text(self) -> str:
        return "What Python runtime version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Python runtime affects package compatibility, performance, and available features.

- Newer versions have better performance but may have compatibility issues
- Some packages only support specific versions
- match statements require 3.10+, walrus operator requires 3.8+"""

    @property
    def options(self) -> list[str]:
        return ["3.14", "3.13", "3.12", "3.11", "3.10", "pypy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.14": "Latest - newest features, may have limited package support",
            "3.13": "Very recent - excellent performance, good feature set",
            "3.12": "Stable - proven performance, wide package compatibility",
            "3.11": "Mature - excellent performance improvements over 3.10",
            "3.10": "Legacy - pattern matching (match/case), better error messages",
            "pypy": "JIT compiler - faster for long-running processes, good for servers",
        }

    @property
    def default(self) -> str:
        return "3.12"
