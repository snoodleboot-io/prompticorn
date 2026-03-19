# Clojure version question

from promptosaurus.questions.base.question import Question


class ClojureVersionQuestion(Question):
    """Question handler for Clojure version."""

    @property
    def key(self) -> str:
        return "clojure_version"

    @property
    def question_text(self) -> str:
        return "What Clojure version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Clojure version determines language features and library compatibility.

- Newer versions have improved performance and new features
- Clojure runs on the JVM for excellent interoperability with Java
- Version affects which Java versions are supported"""
