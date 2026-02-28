# Groovy version question

from promptcli.questions.base.question import Question


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

    @property
    def options(self) -> list[str]:
        return ["4.0", "3.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "4.0": "Latest stable - modern features, recommended for new projects",
            "3.0": "Previous stable - widely supported, battle-tested",
        }

    @property
    def default(self) -> str:
        return "4.0"
