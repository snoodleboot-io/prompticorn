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
        return ["8.0", "7.0", "6.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "8.0": "Latest stable - best features, recommended for new projects",
            "7.0": "Recent stable - excellent all-around",
            "6.0": "Long-term support - maximum compatibility",
        }

    @property
    def default(self) -> str:
        return "8.0"
