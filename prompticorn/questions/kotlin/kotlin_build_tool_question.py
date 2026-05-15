# Kotlin build tool question

from prompticorn.questions.base.question import Question


class KotlinBuildToolQuestion(Question):
    """Question handler for Kotlin build tool."""

    @property
    def key(self) -> str:
        return "kotlin_build_tool"

    @property
    def question_text(self) -> str:
        return "What build tool do you want to use for Kotlin?"

    @property
    def explanation(self) -> str:
        return """Build tools manage dependencies, compilation, and project lifecycle.

- Gradle is the modern standard with excellent Kotlin DSL support
- Maven is mature, widely used in enterprise environments"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["Gradle", "Maven", "Bazel"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "Gradle"

    config_key = "build_tool"
