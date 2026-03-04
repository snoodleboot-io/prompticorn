# Java version question

from promptosaurus.questions.base.question import Question


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
        return ["21", "17", "11", "8"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "21": "Latest LTS - virtual threads, pattern matching, sequenced collections, recommended",
            "17": "Mature LTS - sealed classes, pattern matching for switch, widely adopted",
            "11": "Legacy LTS - first modular JDK, var for local variables, still widely used",
            "8": "Classic - lambdas, streams, maximum compatibility, minimal language changes",
        }

    @property
    def default(self) -> str:
        return "21"
