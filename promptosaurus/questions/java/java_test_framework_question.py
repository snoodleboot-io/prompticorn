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
