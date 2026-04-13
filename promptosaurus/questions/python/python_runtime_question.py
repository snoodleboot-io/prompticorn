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
        return ["3.14", "3.13", "3.12", "3.11", "pypy"]

    @property
    def default(self) -> str:
        return "3.14"

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.14": "Python 3.14 - Latest release with cutting-edge features and performance (recommended)",
            "3.13": "Python 3.13 - Recent release with modern features",
            "3.12": "Python 3.12 - Stable release with improved performance",
            "3.11": "Python 3.11 - Older stable release, good for maximum compatibility",
            "pypy": "PyPy - Alternative Python implementation with JIT for faster execution",
        }
