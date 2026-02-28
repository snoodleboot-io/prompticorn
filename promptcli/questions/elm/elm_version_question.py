# Elm version question

from promptcli.questions.base.question import Question


class ElmVersionQuestion(Question):
    """Question handler for Elm version."""

    @property
    def key(self) -> str:
        return "elm_version"

    @property
    def question_text(self) -> str:
        return "What Elm version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Elm version determines language features and package compatibility.

- Elm 0.19 is the current major version with significant improvements
- It features a smaller runtime, faster compilation, and better error messages
- The Elm architecture provides a reliable frontend development experience"""

    @property
    def options(self) -> list[str]:
        return ["0.19"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "0.19": "Current stable - smaller runtime, faster builds, no runtime exceptions",
        }

    @property
    def default(self) -> str:
        return "0.19"
