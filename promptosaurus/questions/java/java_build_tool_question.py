# Java build tool question

from promptosaurus.questions.base.question import Question


class JavaBuildToolQuestion(Question):
    """Question for Java build tool selection."""

    @property
    def key(self) -> str:
        return "java_build_tool"

    @property
    def question_text(self) -> str:
        return "What build tool do you want to use for Java?"

    @property
    def explanation(self) -> str:
        return """Build tool affects dependency management, build configuration, and project structure.

- Maven: XML-based, convention over configuration, large ecosystem
- Gradle: Groovy/Kotlin DSL, flexible, incremental builds, modern
- Ant: XML-based, imperative, low-level control, older projects"""

    @property
    def options(self) -> list[str]:
        return ["maven", "gradle", "ant"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "maven": "Convention over config - XML-based, vast plugin ecosystem, widely used",
            "gradle": "Flexible and modern - Groovy/Kotlin DSL, incremental builds, Android standard",
            "ant": "Low-level control - XML-based, imperative, older projects, manual configuration",
        }

    @property
    def default(self) -> str:
        return "maven"
