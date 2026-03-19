# Elixir version question

from promptosaurus.questions.base.question import Question


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
