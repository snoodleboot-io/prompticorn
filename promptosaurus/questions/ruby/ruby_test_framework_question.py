# Ruby test framework question

from promptosaurus.questions.base.question import Question


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
