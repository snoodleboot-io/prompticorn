"""Question for selecting TypeScript version."""

from promptosaurus.questions.base.question import Question


class TypeScriptVersionQuestion(Question):
    """Question handler for TypeScript version selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "typescript_version"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What TypeScript version?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select the TypeScript version your project targets."

    @property
    def options(self) -> list[str]:
        """Available TypeScript versions."""
        return ["v6.0", "v5.9", "v5.8", "v5.4", "v5.0"]

    @property
    def default(self) -> str:
        """Default version selection."""
        return "v6.0"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "v6.0": "Latest version with newest features (2025)",
            "v5.9": "Recent stable release",
            "v5.8": "Proven stability and compatibility",
            "v5.4": "Earlier stable version",
            "v5.0": "Legacy support version",
        }
