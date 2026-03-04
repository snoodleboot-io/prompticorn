# Java test framework question

from promptosaurus.questions.base.question import Question


class JavaTestFrameworkQuestion(Question):
    """Question for Java test framework selection."""

    @property
    def key(self) -> str:
        return "java_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written and organized:
- junit5: Modern, extensible, parameterized tests, modern Java features
- junit4: Classic, stable, widely used, mature ecosystem
- testng: Flexible, powerful annotations, parallel execution, data providers"""

    @property
    def options(self) -> list[str]:
        return ["junit5", "junit4", "testng"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "junit5": "Modern standard - extensible architecture, parameterized tests, modern Java",
            "junit4": "Classic - stable, mature ecosystem, annotations-based, widely adopted",
            "testng": "Flexible - powerful data providers, parallel execution, configuration options",
        }

    @property
    def default(self) -> str:
        return "junit5"
