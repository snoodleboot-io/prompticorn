# Handler for single-language repository questions

from typing import Any

import click

from promptosaurus.config_handler import create_default_config
from promptosaurus.questions.base.question import Question
from promptosaurus.questions.language import LANGUAGE_KEYS, get_language_questions


class HandleSingleLanguageQuestions:
    """
    Handler for single-language repository questions.

    This handler prompts the user to select a primary language,
    then asks all language-specific questions from the pipeline.
    """

    def __init__(self, ui_selector: Any) -> None:
        """
        Initialize with a UI selector function.

        Args:
            ui_selector: Function to use for interactive selection
        """
        self.select_option = ui_selector

    def handle(self, repo_type: str) -> dict[str, Any]:
        """
        Handle single-language repository questions.

        Args:
            repo_type: The repository type (should be REPO_TYPE_SINGLE)

        Returns:
            Configuration dictionary with user responses
        """
        # Select primary language
        click.echo("\n\nSelect your primary language:")
        language = self.select_option(
            question="What is your primary language?",
            options=LANGUAGE_KEYS,
            explanations={},
            question_explanation="Select the primary language for your project",
            default_index=LANGUAGE_KEYS.index("python") if "python" in LANGUAGE_KEYS else 0,
        )

        # Get language-specific questions from pipeline
        lang_questions = get_language_questions(language)
        config = create_default_config(language, repo_type=repo_type)

        # Ask each question in the pipeline
        for q in lang_questions:
            value = self._ask_question(q, language)
            config_key = q.key.replace(f"{language}_", "")
            config["defaults"][config_key] = value

        return config

    def _ask_question(self, question: Question, language: str) -> Any:
        """
        Ask a single question and return the response.

        Args:
            question: The question to ask
            language: The selected programming language

        Returns:
            The user's response
        """
        default_idx = (
            question.options.index(question.default) if question.default in question.options else 0
        )
        allow_multiple = getattr(question, "allow_multiple", False)
        default_indices = (
            question.default_indices if hasattr(question, "default_indices") else {default_idx}
        )

        return self.select_option(
            question=question.question_text,
            options=question.options,
            explanations=question.option_explanations,
            question_explanation=question.explanation,
            default_index=default_idx,
            default_indices=default_indices,
            allow_multiple=allow_multiple,
        )
