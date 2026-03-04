# Scala version question

from promptosaurus.questions.base.question import Question


class ScalaVersionQuestion(Question):
    """Question handler for Scala version."""

    @property
    def key(self) -> str:
        return "scala_version"

    @property
    def question_text(self) -> str:
        return "What Scala version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Scala version affects language features and library compatibility.

- Scala 3.x has significant syntax changes and improved type inference
- Scala 2.13 is the last 2.x release with maximum ecosystem compatibility
- Newer versions have better performance and cleaner syntax"""

    @property
    def options(self) -> list[str]:
        return ["3.3", "3.2", "2.13"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.3": "Latest stable Scala 3 - best features, recommended for new projects",
            "3.2": "Stable Scala 3 - excellent type system improvements",
            "2.13": "Last 2.x release - maximum library compatibility",
        }

    @property
    def default(self) -> str:
        return "3.3"
