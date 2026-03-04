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
        return ["5.4", "5.3", "5.2", "5.1", "5.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "5.4": "Latest stable - best inference, const type params, recommended",
            "5.3": "Recent stable - excellent all-around",
            "5.2": "Stable - decorators,/modifiers, narrowing",
            "5.1": "Long-term support - very stable, maximum compatibility",
            "5.0": "Major release - significant changes, may need updates",
        }

    @property
    def default(self) -> str:
        return "5.4"
