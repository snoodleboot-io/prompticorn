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
        """Available options."""
        return [".NET 8", ".NET 7", ".NET Framework 4.8", "Mono"]

    @property
    def default(self) -> str:
        """Default selection."""
        return ".NET 8"

    config_key = "framework"
