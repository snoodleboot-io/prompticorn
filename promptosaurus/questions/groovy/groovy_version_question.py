# Groovy version question

from promptosaurus.questions.base.question import Question


class GroovyVersionQuestion(Question):
    """Question handler for Groovy version."""

    @property
    def key(self) -> str:
        return "groovy_version"

    @property
    def question_text(self) -> str:
        return "What Groovy version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Groovy version affects language features and JVM compatibility.

- Groovy 4.x has modern features and improved performance
- Groovy runs on the JVM with Java interoperability
- Version affects available language features and libraries"""
