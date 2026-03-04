# Swift test framework question

from promptosaurus.questions.base.question import Question


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
        return ["xctest", "quick"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "xctest": "Apple official - integrated with Xcode, XCTestCase, recommended",
            "quick": "BDD style - RSpec-inspired, Nimble matchers, behavior-driven",
        }

    @property
    def default(self) -> str:
        return "xctest"
