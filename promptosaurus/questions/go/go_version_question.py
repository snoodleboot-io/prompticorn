# Go version question

from promptosaurus.questions.base.question import Question


class GoVersionQuestion(Question):
    """Question handler for Go version selection."""

    @property
    def key(self) -> str:
        return "go_version"

    @property
    def question_text(self) -> str:
        return "What Go version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Go version affects module compatibility, performance, and language features.

- Newer versions have better performance and runtime improvements
- Go modules (go.mod) became the standard in 1.13+
- Generics support was added in Go 1.18
- Some libraries require minimum Go versions"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["1.22", "1.21", "1.20", "1.19"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "1.22"

    config_key = "runtime"
