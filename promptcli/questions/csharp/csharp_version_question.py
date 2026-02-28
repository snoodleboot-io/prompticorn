# C# version question

from promptcli.questions.base.question import Question


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
        return ["12", "11", "10", "9"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "12": "Latest - collection expressions, inline arrays, primary constructors, recommended",
            "11": "Recent - raw string literals, required members, generic math, UTF-8 strings",
            "10": "Stable - global usings, file-scoped namespaces, record structs",
            "9": "Mature - records, init-only properties, pattern matching enhancements",
        }

    @property
    def default(self) -> str:
        return "12"
