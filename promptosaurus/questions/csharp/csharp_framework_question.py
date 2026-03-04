# C# framework question

from promptosaurus.questions.base.question import Question


class CSharpFrameworkQuestion(Question):
    """Question for .NET framework version selection."""

    @property
    def key(self) -> str:
        return "csharp_framework"

    @property
    def question_text(self) -> str:
        return "What .NET version do you want to use?"

    @property
    def explanation(self) -> str:
        return """.NET version determines runtime capabilities, library support, and deployment options.

- .NET 8 is the latest LTS with significant performance improvements
- .NET versions ship annually with even-numbered versions being LTS
- Match your target framework to your deployment environment"""

    @property
    def options(self) -> list[str]:
        return [".net8", ".net7", ".net6"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            ".net8": "Latest LTS - significant performance improvements, Aspire, time abstraction, recommended",
            ".net7": "STS - performance improvements, required members, generic math support",
            ".net6": "Mature LTS - file-scoped namespaces, global usings, minimal APIs, hot reload",
        }

    @property
    def default(self) -> str:
        return ".net8"
