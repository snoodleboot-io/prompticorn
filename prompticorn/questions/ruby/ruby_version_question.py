# Ruby version question

from prompticorn.questions.base.question import Question


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

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["3.3", "3.2", "3.1", "3.0", "2.7"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "3.3"

    config_key = "runtime"
