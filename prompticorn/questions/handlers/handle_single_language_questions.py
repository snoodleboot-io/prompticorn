"""Handler for single-language repository question flow.

This module defines the HandleSingleLanguageQuestions class which
manages the question flow for single-language repositories. It
prompts users to select a primary language and then asks all
language-specific questions from the configured pipeline.

The handler coordinates:
1. Language selection from supported languages
2. Loading of core questions for the selected language
3. Presentation of each question to gather user preferences
4. Compilation of responses into a configuration dictionary
"""

from typing import Any

import click

from prompticorn.config_handler import create_default_config
from prompticorn.questions.base.question import Question
from prompticorn.questions.language import LANGUAGE_KEYS, get_language_questions


class HandleSingleLanguageQuestions:
    """Handler for single-language repository questions.

    This handler manages the interactive question flow for users setting up
    a single-language project. It guides users through language selection
    and then presents language-specific configuration questions.

    The handler ensures a smooth user experience by:
    - Prompting for language selection first
    - Loading only relevant questions for the selected language
    - Collecting user responses in the proper configuration format
    - Returning a properly formatted configuration dictionary

    Attributes:
        select_option: Function for interactive option selection in the UI
    """

    def __init__(self, ui_selector: Any) -> None:
        """Initialize with a UI selector function.

        Args:
            ui_selector: Function to use for interactive selection.
                        Should accept question, options, explanations,
                        question_explanation, and default_index parameters.
        """
        self.select_option = ui_selector

    def handle(self, repo_type: str) -> dict[str, Any]:
        """Handle single-language repository questions.

        Guides the user through the single-language setup flow:
        1. Selects primary programming language
        2. Loads language-specific questions
        3. Asks each question and collects responses
        4. Returns complete configuration dictionary

        Args:
            repo_type: The repository type (typically "single-language")

        Returns:
            Configuration dictionary with user responses in the format:
            {
                "version": "1.0",
                "repository": {"type": repo_type},
                "spec": {
                    "language": selected_language,
                    ...language-specific settings...
                }
            }

        Raises:
            UserCancelledError: If user cancels the flow at any point
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
            config["spec"][config_key] = value

        return config

    def _ask_question(self, question: Question, language: str) -> Any:
        """Ask a single question and return the response.

        Presents a single configuration question to the user via the UI
        and collects their response. Handles both single-select and
        multi-select questions with proper default values.

        Args:
            question: The question to ask (should have question_text,
                     options, explanations, and explanation attributes)
            language: The selected programming language (for context only)

        Returns:
            The user's response value(s), which can be a string,
            list of strings, or None depending on the question type

        Raises:
            UserCancelledError: If user cancels the question
        """
        default_idx = (
            question.options.index(question.default) if question.default in question.options else 0
        )

        # Use properties directly - they're defined in Question base class
        allow_multiple = question.allow_multiple
        default_indices = question.default_indices
        none_index = question.none_index

        return self.select_option(
            question=question.question_text,
            options=question.options,
            explanations=question.option_explanations,
            question_explanation=question.explanation,
            default_index=default_idx,
            default_indices=default_indices,
            allow_multiple=allow_multiple,
            none_index=none_index,
        )
