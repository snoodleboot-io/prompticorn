# TypeScript framework question

from promptosaurus.questions.base.question import Question


class TypeScriptFrameworkQuestion(Question):
    """Question for TypeScript framework (React, Vue, etc)."""

    @property
    def key(self) -> str:
        return "typescript_framework"

    @property
    def question_text(self) -> str:
        return "What frontend framework are you using?"

    @property
    def explanation(self) -> str:
        return """Frontend framework affects:
- Component structure
- State management patterns
- Build configuration
- Type definitions needed"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["React", "Vue", "Angular", "Svelte", "None"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "React"

    config_key = "framework"
