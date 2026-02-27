# Python runtime question

from promptcli.questions.base import Question


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
        return ["3.12", "3.11", "3.10", "3.9", "pypy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.12": "Latest stable - best performance, recommended for new projects",
            "3.11": "Very stable - excellent performance improvements over 3.10",
            "3.10": "Stable - pattern matching (match/case), better error messages",
            "3.9": "Long-term support - maximum package compatibility",
            "pypy": "JIT compiler - faster for long-running processes, good for servers",
        }

    @property
    def default(self) -> str:
        return "3.12"
