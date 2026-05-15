# Java version question

from prompticorn.questions.base.question import Question


class JavaVersionQuestion(Question):
    """Question handler for Java version selection."""

    @property
    def key(self) -> str:
        return "java_version"

    @property
    def question_text(self) -> str:
        return "What Java version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Java version affects language features, performance, and library compatibility.

- Newer versions have better performance and modern language features
- LTS (Long Term Support) versions receive updates for many years
- Some libraries require minimum Java versions
- Java 21 is the latest LTS with virtual threads and improved pattern matching"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["21 (LTS)", "17 (LTS)", "11 (LTS)", "8 (LTS)"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "21 (LTS)"

    config_key = "runtime"
