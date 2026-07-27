# Kotlin version question

from prompticorn.questions.base.question import Question


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
        """Available options."""
        return ["2.4", "2.3", "2.2", "2.1", "2.0", "1.9", "1.8", "1.7", "1.6"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "2.4"

    config_key = "runtime"
