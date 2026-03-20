"""Question for Python test framework selection."""

from promptosaurus.questions.base.question import Question


class PythonTestFrameworkQuestion(Question):
    """Question for Python test framework (how tests are written)."""

    @property
    def key(self) -> str:
        return "python_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def options(self) -> list[str]:
        return ["hybrid", "pytest", "unittest"]

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written:
- hybrid: unittest.TestCase with limited pytest fixtures and mocking
- pytest: Industry standard, powerful fixtures, great reporting
- unittest: Built-in, simple, no dependencies"""
