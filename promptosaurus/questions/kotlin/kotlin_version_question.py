# Kotlin version question

from promptosaurus.questions.base.question import Question


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
