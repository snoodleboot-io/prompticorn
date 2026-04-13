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
        option_explanations: Detailed explanations for each version
        default: Default version selection
        config_key: Configuration key where answer is stored
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_runtime"

    @property
    def question_text(self) -> str:
        """The question text to display."""
        return "What Python runtime version?"

    @property
    def explanation(self) -> str:
        """Explanation of why this question matters."""
        return """Select the Python version your project targets.

Python versions affect:
- Available language features and syntax
- Compatible runtimes (CPython, PyPy, etc.)
- Performance characteristics
- Standard library capabilities"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["3.14", "3.13", "3.12", "3.11", "pypy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Detailed explanations for each version."""
        return {
            "3.11": "Python 3.11 - Older stable release, good for maximum compatibility",
            "3.12": "Python 3.12 - Stable release with improved performance",
            "3.13": "Python 3.13 - Recent release with modern features",
            "3.14": "Python 3.14 - Latest release with cutting-edge features and performance (recommended)",
            "pypy": "PyPy - Alternative Python implementation with JIT for faster execution",
        }

    @property
    def default(self) -> str:
        """Default selection."""
        return "3.14"

    config_key = "runtime"
