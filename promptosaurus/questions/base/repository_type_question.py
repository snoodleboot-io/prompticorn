"""Question for determining repository structure type."""

from promptosaurus.questions.base.constants import RepositoryTypes
from promptosaurus.questions.base.question import Question


class RepositoryTypeQuestion(Question):
    """Question for determining repository structure type.

    This question helps configure how language conventions are applied
    based on whether the project uses a single language, multi-language
    monorepo, or mixed collocation structure. The answer affects which
    convention files are included in the prompts and how language-specific
    settings are applied across the codebase.

    Repository structure determines:
    - Which convention files are loaded (single vs multiple language configs)
    - How folder-specific questions are handled
    - Whether language settings apply globally or per-folder

    Attributes:
        key: Unique identifier for this question
        question_text: The question presented to the user
        explanation: Detailed explanation of repository types
        options: Available repository types
        option_explanations: Details for each option
        default: Default selection
        config_key: Configuration key where answer is stored
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "repository_type"

    @property
    def question_text(self) -> str:
        """The question text to display."""
        return "What type of repository is this?"

    @property
    def explanation(self) -> str:
        """Explanation of why this question matters."""
        return "Choose how your codebase is structured linguistically."

    @property
    def options(self) -> list[str]:
        """Available options."""
        return [
            RepositoryTypes.SINGLE,
            RepositoryTypes.MULTI_MONOREPO,
            RepositoryTypes.MIXED,
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Details for each option."""
        return {
            RepositoryTypes.SINGLE: "Single language for the entire project",
            RepositoryTypes.MULTI_MONOREPO: "Multiple languages in different folders (monorepo)",
            RepositoryTypes.MIXED: "Mixed collocation - multiple languages in the same directories",
        }

    @property
    def default(self) -> str:
        """Default selection."""
        return RepositoryTypes.SINGLE

    config_key = "repository.type"
