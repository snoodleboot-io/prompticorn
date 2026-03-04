# Swift package manager question

from promptosaurus.questions.base.question import Question


class SwiftPackageManagerQuestion(Question):
    """Question handler for Swift package manager."""

    @property
    def key(self) -> str:
        return "swift_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for Swift?"

    @property
    def explanation(self) -> str:
        return """Package managers handle dependency resolution and project structure.

- SPM is the official Swift Package Manager, integrated with Xcode
- CocoaPods has extensive library support for iOS/macOS
- Carthage is decentralized and builds dependencies as frameworks"""

    @property
    def options(self) -> list[str]:
        return ["spm", "cocoapods", "carthage"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "spm": "Official - integrated with Xcode, modern, recommended for new projects",
            "cocoapods": "Mature ecosystem - extensive library support, widely used in iOS",
            "carthage": "Decentralized - builds frameworks, no central server needed",
        }

    @property
    def default(self) -> str:
        return "spm"
