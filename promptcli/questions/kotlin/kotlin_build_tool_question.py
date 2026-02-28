# Kotlin build tool question

from promptcli.questions.base.question import Question


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
        return ["gradle", "maven"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "gradle": "Modern standard - excellent Kotlin DSL, flexible, fast incremental builds",
            "maven": "Mature enterprise - declarative, extensive plugin ecosystem",
        }

    @property
    def default(self) -> str:
        return "gradle"
