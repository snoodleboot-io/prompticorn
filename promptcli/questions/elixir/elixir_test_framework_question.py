# Elixir test framework question

from promptcli.questions.base.question import Question


class ElixirTestFrameworkQuestion(Question):
    """Question handler for Elixir test framework."""

    @property
    def key(self) -> str:
        return "elixir_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Elixir?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure and assertions for testing.

- ExUnit is the built-in testing framework for Elixir
- It provides expressive assertions and test organization
- No additional dependencies needed as it's included with Elixir"""

    @property
    def options(self) -> list[str]:
        return ["exunit"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "exunit": "Built-in Elixir testing - expressive, no external dependencies",
        }

    @property
    def default(self) -> str:
        return "exunit"
