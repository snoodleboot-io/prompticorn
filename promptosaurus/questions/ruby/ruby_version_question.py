# Ruby version question

from promptosaurus.questions.base.question import Question


class RubyVersionQuestion(Question):
    """Question handler for Ruby version."""

    @property
    def key(self) -> str:
        return "ruby_version"

    @property
    def question_text(self) -> str:
        return "What Ruby version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Ruby version affects performance, security patches, and available features.

- Newer versions have better performance and security updates
- Ruby 3.x has significant performance improvements (Ruby 3x3 initiative)
- Some gems may not support older versions"""
