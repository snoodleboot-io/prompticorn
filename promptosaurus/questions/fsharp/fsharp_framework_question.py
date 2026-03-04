# F# framework question

from promptosaurus.questions.base.question import Question


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
        return [".net8", ".net7", ".net6"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            ".net8": ".NET 8 LTS - latest long-term support, best performance, recommended",
            ".net7": ".NET 7 - recent release with new features",
            ".net6": ".NET 6 LTS - stable, widely deployed",
        }

    @property
    def default(self) -> str:
        return ".net8"
