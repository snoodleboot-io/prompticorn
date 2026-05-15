# Rust test framework question

from prompticorn.questions.base.question import Question


class RustTestFrameworkQuestion(Question):
    """Question for Rust testing approach selection."""

    @property
    def key(self) -> str:
        return "rust_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing approach do you want to use for Rust?"

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written and organized:
- built-in: Rust's native test framework with `#[test]` attribute, no dependencies
- criterion: Statistics-driven benchmarking and testing library for thorough performance tests"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["built-in", "criterion", "quickcheck"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "built-in"

    config_key = "test_framework"
