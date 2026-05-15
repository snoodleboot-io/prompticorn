# F# framework question

from prompticorn.questions.base.question import Question


class FSharpFrameworkQuestion(Question):
    """Question handler for F# .NET framework version."""

    @property
    def key(self) -> str:
        return "fsharp_framework"

    @property
    def question_text(self) -> str:
        return "What .NET framework version do you want to target?"

    @property
    def explanation(self) -> str:
        return """.NET framework version determines available APIs and runtime capabilities.

- .NET 8 is the latest LTS release with significant performance improvements
- F# runs on .NET with full access to the ecosystem
- Framework version affects deployment and compatibility"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return [".NET 8", ".NET 7", "Mono"]

    @property
    def default(self) -> str:
        """Default selection."""
        return ".NET 8"

    config_key = "framework"
