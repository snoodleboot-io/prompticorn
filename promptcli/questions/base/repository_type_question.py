# Repository type question

from promptcli.questions.base.question import Question


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
        return ["single-language", "multi-language-folder", "mixed"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "single-language": "One language in the entire codebase (e.g., pure Python, TypeScript only)",
            "multi-language-folder": "Different languages in different folders (e.g., /frontend=TypeScript, /backend=Python)",
            "mixed": "Multiple languages mixed in the same folders (rare, complex setups)",
        }

    @property
    def default(self) -> str:
        return "single-language"
