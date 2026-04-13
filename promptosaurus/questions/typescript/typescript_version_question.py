"""Question for selecting TypeScript version.

This module defines the TypeScriptVersionQuestion class which prompts
users to select their desired TypeScript version. This affects
available language features, type system capabilities, and
ecosystem compatibility.
"""

from promptosaurus.questions.base.question import Question


class TypeScriptVersionQuestion(Question):
    """Question handler for TypeScript version selection.

    This question asks users to select their preferred TypeScript
    version, which determines available language features, type system
    capabilities, and compiler behavior. The selection affects which
    TypeScript-specific conventions and best practices are applied
    to the project configuration.

    Options range from the latest TypeScript 6.x to earlier 5.x releases,
    balancing modern features against ecosystem compatibility.

    Attributes:
        question_text: The question presented to the user
        explanation: Detailed explanation of TypeScript versions
        options: Available TypeScript versions
        default: Default version selection
        config_key: Configuration key where answer is stored
    """

    question_text = "What TypeScript version?"
    explanation = "Select the TypeScript version your project targets."
    options = ["5.0", "5.1", "5.2", "5.3", "5.4"]
    default = "5.4"
    config_key = "runtime"
