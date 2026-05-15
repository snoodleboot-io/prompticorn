# Swift test framework question

from prompticorn.questions.base.question import Question


class SwiftTestFrameworkQuestion(Question):
    """Question handler for Swift test framework."""

    @property
    def key(self) -> str:
        return "swift_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Swift?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure for writing and running tests.

- XCTest is Apple's official testing framework, integrated with Xcode
- Quick is a BDD-style framework inspired by RSpec"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["XCTest", "Quick/Nimble", "Spectre"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "XCTest"

    config_key = "test_framework"
