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
