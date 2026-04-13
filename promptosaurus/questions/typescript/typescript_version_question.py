# TypeScript version question

from promptosaurus.questions.base.question import Question


class TypeScriptVersionQuestion(Question):
    """Question handler for TypeScript version."""

    @property
    def key(self) -> str:
        return "typescript_version"

    @property
    def question_text(self) -> str:
        return "What TypeScript version do you want to use?"

    @property
    def explanation(self) -> str:
        return """TypeScript version affects available features and type system capabilities.

- Newer versions have better inference and more features
- Older versions have better ecosystem compatibility"""

    @property
    def options(self) -> list[str]:
        return ["6.0", "5.9", "5.8", "5.7", "5.6", "5.5", "5.4", "5.3", "5.2", "5.1", "5.0"]

    @property
    def default(self) -> str:
        return "6.0"

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "6.0": "TypeScript 6.0 - Latest major release (recommended)",
            "5.9": "TypeScript 5.9 - Latest 5.x release",
            "5.8": "TypeScript 5.8 - Stable 5.x release",
            "5.7": "TypeScript 5.7 - Stable 5.x release",
            "5.6": "TypeScript 5.6 - Stable 5.x release",
            "5.5": "TypeScript 5.5 - Stable 5.x release",
            "5.4": "TypeScript 5.4 - Stable 5.x release",
            "5.3": "TypeScript 5.3 - Stable 5.x release",
            "5.2": "TypeScript 5.2 - Older 5.x release",
            "5.1": "TypeScript 5.1 - Older 5.x release",
            "5.0": "TypeScript 5.0 - First 5.x release",
        }
