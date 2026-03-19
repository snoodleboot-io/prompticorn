# TypeScript package manager question

from promptosaurus.questions.base.question import Question


class TypeScriptPackageManagerQuestion(Question):
    """Question for TypeScript package manager."""

    @property
    def key(self) -> str:
        return "typescript_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for JavaScript/TypeScript?"

    @property
    def explanation(self) -> str:
        return """Package manager affects:
- Installation speed
- Lock file handling
- Workspace support
- Node version management"""
