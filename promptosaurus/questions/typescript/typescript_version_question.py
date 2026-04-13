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
        key: Unique identifier for this question
        question_text: The question presented to the user
        explanation: Detailed explanation of TypeScript versions
        options: Available TypeScript versions
        default: Default version selection
        config_key: Configuration key where answer is stored
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "typescript_version"

    @property
    def question_text(self) -> str:
        """The question text to display."""
        return "What TypeScript version?"

    @property
    def explanation(self) -> str:
        """Explanation of why this question matters."""
        return "Select the TypeScript version your project targets."

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["v6.0", "v5.9", "v5.8", "v5.4", "v5.0"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "v6.0"

    config_key = "runtime"
