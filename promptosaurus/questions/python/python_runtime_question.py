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
        question_text: The question presented to the user
        explanation: Detailed explanation of Python versions
        options: Available Python runtime versions
        default: Default version selection
        config_key: Configuration key where answer is stored
    """

    question_text = "What Python runtime version?"
    explanation = "Select the Python version your project targets."
    options = ["3.10", "3.11", "3.12", "3.13", "3.14"]
    default = "3.12"
    config_key = "runtime"
