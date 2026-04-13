# Go test framework question

from promptosaurus.questions.base.question import Question


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
        """Available options."""
        return ["testing (stdlib)", "testify", "ginkgo"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "testing (stdlib)"

    config_key = "test_framework"
