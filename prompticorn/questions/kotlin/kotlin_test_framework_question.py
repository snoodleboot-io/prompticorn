# Kotlin test framework question

from prompticorn.questions.base.question import Question


class KotlinTestFrameworkQuestion(Question):
    """Question for Kotlin test framework selection."""

    @property
    def key(self) -> str:
        return "kotlin_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written, organized, and executed:
- JUnit5: The standard JVM test runner; works everywhere, great tooling
- Kotest: Kotlin-first framework with expressive specs, matchers, and property testing
- Spek: BDD-style specification framework for Kotlin"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["JUnit5", "Kotest", "Spek"]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Detailed explanations for each framework."""
        return {
            "JUnit5": "The standard JVM test runner; works everywhere, great tooling",
            "Kotest": "Kotlin-first framework with expressive specs, matchers, property testing",
            "Spek": "BDD-style specification framework for Kotlin",
        }

    @property
    def default(self) -> str:
        """Default selection."""
        return "JUnit5"

    config_key = "test_framework"
