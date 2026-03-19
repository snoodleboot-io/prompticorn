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
