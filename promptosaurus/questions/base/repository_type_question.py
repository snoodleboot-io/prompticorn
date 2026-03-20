"""Question for repository structure type selection."""

from promptosaurus.questions.base.question import Question


class RepositoryTypeQuestion(Question):
    """Question about repository structure."""

    @property
    def key(self) -> str:
        return "repository_type"

    @property
    def question_text(self) -> str:
        return "What is your repository structure?"

    @property
    def explanation(self) -> str:
        return """This determines how language conventions are applied.

Single language: One codebase (e.g., pure Python project)
Multi-language folder: Separate folders with different languages (e.g., /frontend, /backend)
Mixed: Multiple languages in the same folder

This affects which convention files are included in your prompts."""

    @property
    def options(self) -> list[str]:
        return ["single-language", "multi-language-monorepo", "mixed-collocation"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "single-language": "Single language: One codebase (e.g., pure Python project)",
            "multi-language-monorepo": "Multi-language folder: Separate folders with different languages (e.g., /frontend, /backend)",
            "mixed-collocation": "Mixed: Multiple languages in the same folder",
        }

    @property
    def default(self) -> str:
        return "single-language"
