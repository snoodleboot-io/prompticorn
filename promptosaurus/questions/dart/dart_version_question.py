# Dart version question

from promptosaurus.questions.base.question import Question


class DartVersionQuestion(Question):
    """Question handler for Dart version."""

    @property
    def key(self) -> str:
        return "dart_version"

    @property
    def question_text(self) -> str:
        return "What Dart version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Dart version affects language features and Flutter compatibility.

- Newer versions have improved performance and language features
- Dart powers Flutter for cross-platform mobile and web development
- Version affects available libraries and tooling"""
