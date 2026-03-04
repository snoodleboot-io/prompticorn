# PHP version question

from promptosaurus.questions.base.question import Question


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
        return ["8.3", "8.2", "8.1", "8.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "8.3": "Latest stable - typed class constants, dynamic class const fetch, recommended",
            "8.2": "Recent stable - readonly classes, sensitive parameter redaction",
            "8.1": "Stable - enums, readonly properties, first-class callable syntax",
            "8.0": "Major release - JIT compiler, named arguments, union types",
        }

    @property
    def default(self) -> str:
        return "8.3"
