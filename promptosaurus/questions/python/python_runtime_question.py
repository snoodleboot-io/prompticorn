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
