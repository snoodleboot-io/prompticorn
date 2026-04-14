# PHP test framework question

from promptosaurus.questions.base.question import Question


class PhpTestFrameworkQuestion(Question):
    """Question handler for PHP test framework."""

    @property
    def key(self) -> str:
        return "php_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for PHP?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure for writing and running tests.

- PHPUnit is the industry standard with extensive features
- Pest is a modern alternative with elegant syntax built on PHPUnit"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["PHPUnit", "Pest", "Codeception", "Behat"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "PHPUnit"

    config_key = "test_framework"
