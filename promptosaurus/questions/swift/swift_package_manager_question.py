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
