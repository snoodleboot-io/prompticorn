"""Question for determining repository structure type."""

from promptosaurus.questions.base.question import Question
from promptosaurus.questions.base.constants import RepositoryTypes


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
        question_text: The question presented to the user
        explanation: Detailed explanation of repository types
        options: Available repository types
        option_explanations: Details for each option
        default: Default selection
        config_key: Configuration key where answer is stored
    """

    question_text = "What type of repository is this?"
    explanation = "Choose how your codebase is structured linguistically."

    options = [
        RepositoryTypes.SINGLE,
        RepositoryTypes.MULTI_MONOREPO,
    ]

    option_explanations = {
        RepositoryTypes.SINGLE: "Single language for the entire project",
        RepositoryTypes.MULTI_MONOREPO: "Multiple languages in different folders (monorepo)",
    }

    default = RepositoryTypes.SINGLE
    config_key = "repository.type"
