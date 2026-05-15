# Scala build tool question

from prompticorn.questions.base.question import Question


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
        """Available options."""
        return ["sbt", "Mill", "Maven", "Gradle"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "sbt"

    config_key = "build_tool"
