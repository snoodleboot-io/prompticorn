# C# version question

from promptosaurus.questions.base.question import Question


class CSharpVersionQuestion(Question):
    """Question handler for C# language version selection."""

    @property
    def key(self) -> str:
        return "csharp_version"

    @property
    def question_text(self) -> str:
        return "What C# version do you want to use?"

    @property
    def explanation(self) -> str:
        return """C# version affects available language features and syntax capabilities.

- Newer versions have more concise syntax and powerful features
- Features like records, pattern matching, and nullability were added recently
- Match your C# version to your .NET version for best compatibility"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["12.0", "11.0", "10.0", "9.0"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "12.0"

    config_key = "runtime"
