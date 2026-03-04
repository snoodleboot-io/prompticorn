# Dart test framework question

from promptosaurus.questions.base.question import Question


class DartTestFrameworkQuestion(Question):
    """Question handler for Dart test framework."""

    @property
    def key(self) -> str:
        return "dart_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Dart?"

    @property
    def explanation(self) -> str:
        return """Dart includes a built-in testing framework that covers most needs.

- The built-in test package provides comprehensive testing capabilities
- Supports unit tests, widget tests (for Flutter), and integration tests
- No additional configuration needed as it's included with Dart SDK"""

    @property
    def options(self) -> list[str]:
        return ["built-in"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "built-in": "Dart test package - comprehensive, included with SDK",
        }

    @property
    def default(self) -> str:
        return "built-in"
