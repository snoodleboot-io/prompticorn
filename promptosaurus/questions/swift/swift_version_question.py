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
        return ["5.9", "5.8", "5.7"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "5.9": "Latest stable - macros, improved C++ interop, parameter packs, recommended",
            "5.8": "Recent stable - improved performance, better concurrency",
            "5.7": "Stable - regex literals, concurrency improvements, opaque types",
        }

    @property
    def default(self) -> str:
        return "5.9"
