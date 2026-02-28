# Scala build tool question

from promptcli.questions.base.question import Question


class ScalaBuildToolQuestion(Question):
    """Question handler for Scala build tool."""

    @property
    def key(self) -> str:
        return "scala_build_tool"

    @property
    def question_text(self) -> str:
        return "What build tool do you want to use for Scala?"

    @property
    def explanation(self) -> str:
        return """Build tools manage dependencies, compilation, and project lifecycle.

- sbt is the most popular and idiomatic choice for Scala
- Gradle has better multi-language project support
- Mill is a modern alternative with fast builds"""

    @property
    def options(self) -> list[str]:
        return ["sbt", "gradle", "mill"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "sbt": "Scala build tool - most popular, excellent Scala integration",
            "gradle": "General build tool - good for multi-language projects",
            "mill": "Modern build tool - fast, simple configuration",
        }

    @property
    def default(self) -> str:
        return "sbt"
