# Swift version question

from promptosaurus.questions.base.question import Question


class SwiftVersionQuestion(Question):
    """Question handler for Swift version."""

    @property
    def key(self) -> str:
        return "swift_version"

    @property
    def question_text(self) -> str:
        return "What Swift version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Swift version affects available features, performance, and platform support.

- Newer versions have improved performance and language features
- Swift 5.9+ includes macros and improved C++ interoperability
- Version affects minimum iOS/macOS deployment targets"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["5.9", "5.8", "5.7", "5.6"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "5.9"

    config_key = "runtime"
