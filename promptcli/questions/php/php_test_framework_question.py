# PHP test framework question

from promptcli.questions.base.question import Question


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
        return ["phpunit", "pest"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "phpunit": "Industry standard - xUnit style, extensive assertions, widely used",
            "pest": "Modern elegant - beautiful syntax, built on PHPUnit, growing popularity",
        }

    @property
    def default(self) -> str:
        return "phpunit"
