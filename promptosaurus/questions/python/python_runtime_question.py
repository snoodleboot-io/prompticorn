"""Question for selecting Python runtime version.

This module defines the PythonRuntimeQuestion class which prompts
users to select their desired Python runtime version. This affects
package compatibility, available language features, and performance
characteristics of the project.
"""

from promptosaurus.questions.base.question import Question


class PythonRuntimeQuestion(Question):
    """Question handler for Python runtime/version selection.

    This question asks users to select their preferred Python runtime
    version, which determines language feature availability, package
    compatibility, and performance characteristics. The selection affects
    which Python-specific conventions and best practices are applied
    to the project configuration.

    Available options include recent CPython versions and PyPy, each
    with different trade-offs between cutting-edge features, stability,
    and performance.

    Attributes:
        key: Unique identifier for this question
        question_text: The question presented to the user
        explanation: Detailed explanation of Python versions
        options: Available Python runtime versions
        default: Default version selection
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_runtime"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What Python runtime version?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return (
            "Select the Python version and runtime your project targets.\n"
            "Different Python versions offer different features, performance characteristics,\n"
            "and compatibility with third-party libraries. CPython is the standard implementation,\n"
            "while PyPy offers performance improvements through JIT compilation."
        )

    @property
    def options(self) -> list[str]:
        """Available Python runtime versions."""
        return ["3.14", "3.13", "3.12", "3.11", "pypy"]

    @property
    def default(self) -> str:
        """Default version selection."""
        return "3.14"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "3.11": "Python 3.11 - Older stable release, good for maximum compatibility",
            "3.12": "Python 3.12 - Stable release with improved performance",
            "3.13": "Python 3.13 - Recent release with modern features",
            "3.14": "Python 3.14 - Latest release with cutting-edge features and performance (recommended)",
            "pypy": "PyPy - Alternative Python implementation with JIT for faster execution",
        }
