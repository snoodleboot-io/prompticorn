# TypeScript test framework question

from promptosaurus.questions.base.question import Question


class TypeScriptTestFrameworkQuestion(Question):
    """Question for TypeScript test framework."""

    @property
    def key(self) -> str:
        return "typescript_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Testing framework affects:
- Unit and integration testing
- Mocking capabilities
- Assertion syntax
- Coverage reporting"""
