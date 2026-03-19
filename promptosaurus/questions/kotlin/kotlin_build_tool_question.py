# Kotlin build tool question

from promptosaurus.questions.base.question import Question


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
