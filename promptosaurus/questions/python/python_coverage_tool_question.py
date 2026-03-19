# Python coverage tool question

from promptosaurus.questions.base.question import Question


class PythonCoverageToolQuestion(Question):
    """Question for Python code coverage tool selection."""

    @property
    def key(self) -> str:
        return "coverage_tool"

    @property
    def question_text(self) -> str:
        return "What coverage tool do you want to use?"

    @property
    def explanation(self) -> str:
        return """Coverage tool measures how much of your code is tested:
- pytest-cov: Industry standard, integrates with pytest, widely used
- coverage.py: The classic coverage tool, works with any test runner"""
