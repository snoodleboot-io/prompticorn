# Ruby test framework question

from promptcli.questions.base.question import Question


class RubyTestFrameworkQuestion(Question):
    """Question handler for Ruby test framework."""

    @property
    def key(self) -> str:
        return "ruby_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Ruby?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure for writing and running tests.

- RSpec is behavior-driven with expressive syntax
- Minitest is simpler, built into Ruby stdlib"""

    @property
    def options(self) -> list[str]:
        return ["rspec", "minitest"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "rspec": "Behavior-driven - expressive DSL, great mocking, recommended",
            "minitest": "Built-in - simpler, faster, no dependencies",
        }

    @property
    def default(self) -> str:
        return "rspec"
