# Dart version question

from prompticorn.questions.base.question import Question


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

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["3.3", "3.2", "3.1", "3.0", "2.19"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "3.3"

    config_key = "runtime"
