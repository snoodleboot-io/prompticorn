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
        return ["5.4", "5.x", "5.3", "5.0", "4.x", "3.x"]

    @property
    def default(self) -> str:
        return "5.x"
