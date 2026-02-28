# Kotlin version question

from promptcli.questions.base.question import Question


class KotlinVersionQuestion(Question):
    """Question handler for Kotlin version."""

    @property
    def key(self) -> str:
        return "kotlin_version"

    @property
    def question_text(self) -> str:
        return "What Kotlin version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Kotlin version affects language features, performance, and tooling.

- Newer versions have improved performance and new language features
- Kotlin 1.9+ includes improved K2 compiler and better Java interoperability
- Version affects coroutines stability and compiler optimizations"""

    @property
    def options(self) -> list[str]:
        return ["1.9", "1.8", "1.7"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.9": "Latest stable - K2 compiler improvements, better Java interop, recommended",
            "1.8": "Recent stable - improved build speed, stable Kotlin/Native",
            "1.7": "Stable - definitely non-nullable types, builder inference improvements",
        }

    @property
    def default(self) -> str:
        return "1.9"
