# Dart version question

from promptcli.questions.base.question import Question


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
        return ["3.2", "3.1", "3.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.2": "Latest stable - best features, recommended for new projects",
            "3.1": "Recent stable - excellent all-around",
            "3.0": "Stable - widely supported, maximum compatibility",
        }

    @property
    def default(self) -> str:
        return "3.2"
