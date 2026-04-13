# F# version question

from promptosaurus.questions.base.question import Question


class FSharpVersionQuestion(Question):
    """Question handler for F# version."""

    @property
    def key(self) -> str:
        return "fsharp_version"

    @property
    def question_text(self) -> str:
        return "What F# version do you want to use?"

    @property
    def explanation(self) -> str:
        return """F# version determines language features and .NET compatibility.

- Newer versions have improved type inference and language features
- F# runs on .NET for excellent performance and library access
- Version is typically aligned with .NET releases"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["8.0", "7.0", "6.0", "5.0"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "8.0"

    config_key = "runtime"
