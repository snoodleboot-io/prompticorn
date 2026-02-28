# Go test framework question

from promptcli.questions.base.question import Question


class GoTestFrameworkQuestion(Question):
    """Question for Go testing approach selection."""

    @property
    def key(self) -> str:
        return "go_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing approach do you want to use for Go?"

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written and organized:
- standard: Built-in testing package, simple table-driven tests
- testify: Popular assertion library with mocks and test suites
- ginkgo: BDD-style testing framework with descriptive test structure"""

    @property
    def options(self) -> list[str]:
        return ["standard", "testify", "ginkgo"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "standard": "Built-in testing - table-driven tests, no dependencies, Go idiomatic",
            "testify": "Popular assertions - requires package, rich assertion library with mocks",
            "ginkgo": "BDD style - descriptive test structure, good for complex test suites",
        }

    @property
    def default(self) -> str:
        return "standard"
