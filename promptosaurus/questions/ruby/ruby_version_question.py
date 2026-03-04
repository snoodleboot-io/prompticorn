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

    @property
    def options(self) -> list[str]:
        return ["3.3", "3.2", "3.1", "2.7"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.3": "Latest stable - Prism parser, pure-Ruby IO scheduler, recommended",
            "3.2": "Recent stable - WASI support, faster Proc allocation",
            "3.1": "Stable - YJIT compiler (on x86_64), keyword arguments improvements",
            "2.7": "Legacy - end of life, not recommended for new projects",
        }

    @property
    def default(self) -> str:
        return "3.3"
