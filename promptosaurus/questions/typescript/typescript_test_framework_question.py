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
        return ["vitest", "jest", "mocha"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "vitest": "Fast, modern - Vite-native, great DX, recommended for new projects",
            "jest": "Popular - Facebook-maintained, great ecosystem, widely used",
            "mocha": "Flexible - simple, good for legacy projects",
        }

    @property
    def default(self) -> str:
        return "vitest"
