# Elixir version question

from promptcli.questions.base.question import Question


class ElixirVersionQuestion(Question):
    """Question handler for Elixir version."""

    @property
    def key(self) -> str:
        return "elixir_version"

    @property
    def question_text(self) -> str:
        return "What Elixir version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Elixir version affects language features and compatibility with Erlang/OTP.

- Newer versions have improved tooling and language features
- Elixir runs on the Erlang VM (BEAM) for high concurrency
- Version compatibility affects library availability"""

    @property
    def options(self) -> list[str]:
        return ["1.16", "1.15", "1.14"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.16": "Latest stable - best performance and features, recommended",
            "1.15": "Recent stable - excellent all-around",
            "1.14": "Long-term support - maximum library compatibility",
        }

    @property
    def default(self) -> str:
        return "1.16"
