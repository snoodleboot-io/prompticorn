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

    @property
    def options(self) -> list[str]:
        return ["vitest", "jest"]

    @property
    def default(self) -> str:
        return "vitest"

    @property
    def allow_multiple(self) -> bool:
        return False
