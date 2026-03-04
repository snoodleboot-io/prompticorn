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

    @property
    def options(self) -> list[str]:
        return ["npm", "pnpm", "yarn"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "npm": "Official - largest ecosystem, good for most projects",
            "pnpm": "Fast, efficient - disk space savings, strict node_modules",
            "yarn": "Facebook - good features, widely used, npm alternative",
        }

    @property
    def default(self) -> str:
        return "npm"
