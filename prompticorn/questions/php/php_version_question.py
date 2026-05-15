# PHP version question

from prompticorn.questions.base.question import Question


class PhpVersionQuestion(Question):
    """Question handler for PHP version."""

    @property
    def key(self) -> str:
        return "php_version"

    @property
    def question_text(self) -> str:
        return "What PHP version do you want to use?"

    @property
    def explanation(self) -> str:
        return """PHP version affects performance, security, and available features.

- PHP 8.x has major performance improvements and new features
- JIT compilation was introduced in PHP 8.0
- Named arguments, match expressions, and union types are 8.0+"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["8.3", "8.2", "8.1", "8.0", "7.4"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "8.3"

    config_key = "runtime"
