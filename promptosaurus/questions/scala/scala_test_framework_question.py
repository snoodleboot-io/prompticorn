# Scala test framework question

from promptosaurus.questions.base.question import Question


class ScalaTestFrameworkQuestion(Question):
    """Question handler for Scala test framework."""

    @property
    def key(self) -> str:
        return "scala_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Scala?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide different styles and features for testing.

- ScalaTest is the most comprehensive with multiple testing styles
- MUnit is lightweight and fast
- Specs2 focuses on BDD-style specifications"""

    @property
    def options(self) -> list[str]:
        return ["scalatest", "munit", "specs2"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "scalatest": "Most popular - multiple styles, comprehensive features",
            "munit": "Lightweight - fast, simple, works with all Scala versions",
            "specs2": "BDD-focused - specification-style testing",
        }

    @property
    def default(self) -> str:
        return "scalatest"
