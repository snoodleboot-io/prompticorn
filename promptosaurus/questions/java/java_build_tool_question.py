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
