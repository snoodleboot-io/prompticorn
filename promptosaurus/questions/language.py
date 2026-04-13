"""Language registry and factory functions.

This module provides the language question loading infrastructure for promptosaurus.
It handles loading question pipelines from YAML configuration and instantiating
the appropriate Question classes using the sweet_tea factory pattern.

Functions:
    get_language_questions: Get all questions for a specific language.
    get_core_questions: Get core questions for a language (shared across folders).
    get_fungible_questions: Get fungible questions for a language + folder type.
    _load_pipelines: Load question pipelines from YAML file.

Classes:
    QuestionPipelineError: Exception raised when a question cannot be loaded.

Constants:
    LANGUAGE_KEYS: List of available language keys for dynamic lookup.
"""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.sweet_tea_error import SweetTeaError

from promptosaurus.questions.base.question import Question


class LanguageRegistry:
    """Registry for supported languages.

    Loads supported languages from YAML configuration file and provides
    methods for language validation and lookup.
    """

    _languages: list[str] | None = None

    @classmethod
    def _load_languages(cls) -> list[str]:
        """Load supported languages from YAML file.

        Returns:
            List of supported language keys.
        """
        if cls._languages is None:
            config_file = Path(__file__).parent.parent / "configurations" / "languages.yaml"
            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                cls._languages = data["supported_languages"]
        return cls._languages

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """Get list of all supported languages.

        Returns:
            Copy of supported languages list.
        """
        return cls._load_languages().copy()

    @classmethod
    def is_supported(cls, language: str) -> bool:
        """Check if a language is supported.

        Args:
            language: Language key to check.

        Returns:
            True if language is supported, False otherwise.
        """
        return language.lower() in cls._load_languages()


class QuestionPipelineError(Exception):
    """Raised when a question cannot be loaded from the pipeline.

    This exception is raised when the question pipeline configuration
    references a question class that cannot be loaded or instantiated.

    Attributes:
        class_name: The name of the question class that failed to load.
        language: The language for which the question was being loaded.
        reason: The reason for the failure.
    """

    def __init__(self, class_name: str, language: str, reason: str) -> None:
        """Initialize the error with details.

        Args:
            class_name: The name of the question class that failed.
            language: The language being configured.
            reason: The failure reason.
        """
        self.class_name = class_name
        self.language = language
        self.reason = reason
        super().__init__(
            f"Failed to load question '{class_name}' for language '{language}': {reason}"
        )


# Registry of available language keys for dynamic lookup
# Registry of available language keys for dynamic lookup (loaded from YAML)
LANGUAGE_KEYS = LanguageRegistry.get_supported_languages()


def _load_pipelines() -> dict[str, Any]:
    """Load question pipelines from YAML file.

    Reads the question_pipelines.yaml file which defines which
    question classes should be asked for each language.

    Returns:
        Dictionary mapping language keys to either:
        - List of question class names (backward compat)
        - Dict with 'core' and 'fungible' keys

    Raises:
        FileNotFoundError: If the pipelines YAML file doesn't exist.
        yaml.YAMLError: If the YAML file is malformed.
    """
    pipelines_path = Path(__file__).parent / "question_pipelines.yaml"
    with open(pipelines_path, encoding="utf-8") as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]


def get_core_questions(language: str) -> list[Question]:
    """Get core questions for a specific language.

    Core questions are asked ONCE per language and shared across all folders.

    Args:
        language: The language key (e.g., 'python', 'typescript').

    Returns:
        List of core Question instances.

    Raises:
        QuestionPipelineError: If a question class cannot be loaded.
        ValueError: If the language is not supported.
    """
    questions: list[Question] = []
    lang = language.lower()

    if lang not in LANGUAGE_KEYS:
        raise ValueError(f"Unsupported language: {lang}. Available: {LANGUAGE_KEYS}")

    pipelines = _load_pipelines()
    lang_config = pipelines.get(lang, [])

    # Handle both old format (list) and new format (dict with core/fungible)
    if isinstance(lang_config, list):
        # Old format: just a list of questions (all treated as core)
        question_classes = lang_config
    elif isinstance(lang_config, dict):
        # New format: dict with 'core' and 'fungible'
        question_classes = lang_config.get("core", [])
    else:
        question_classes = []

    # Instantiate each question class
    factory = AbstractFactory[Question]
    for class_name in question_classes:
        try:
            question = factory.create(class_name)
            questions.append(question)
        except SweetTeaError as e:
            raise QuestionPipelineError(
                class_name=class_name,
                language=lang,
                reason=f"Class not registered or not a subclass of BaseQuestion: {e}",
            ) from e

    return questions


def get_fungible_questions(language: str, folder_type: str) -> list[Question]:
    """Get fungible questions for a specific language and folder type.

    Fungible questions are asked for EACH folder and can differ per workspace.

    Args:
        language: The language key (e.g., 'python', 'typescript').
        folder_type: The folder type (e.g., 'backend/api', 'frontend/ui').

    Returns:
        List of fungible Question instances for this language + folder type.
    """
    questions: list[Question] = []
    lang = language.lower()

    if lang not in LANGUAGE_KEYS:
        return []  # No questions for unsupported languages

    pipelines = _load_pipelines()
    lang_config = pipelines.get(lang, {})

    # Handle both old format (list) and new format (dict with core/fungible)
    if isinstance(lang_config, list):
        # Old format: no fungible questions
        return []
    elif isinstance(lang_config, dict):
        fungible_config = lang_config.get("fungible", {})
        if isinstance(fungible_config, dict):
            question_classes = fungible_config.get(folder_type, [])
        else:
            question_classes = []
    else:
        question_classes = []

    # Instantiate each question class
    factory = AbstractFactory[Question]
    for class_name in question_classes:
        try:
            question = factory.create(class_name)
            questions.append(question)
        except SweetTeaError:
            # Skip if question class not found (e.g., not implemented yet)
            pass

    return questions


def get_language_questions(language: str) -> list[Question]:
    """Get all questions for a specific language (core only).

    Loads and instantiates all Question classes defined in the pipeline
    for the given language using the sweet_tea AbstractFactory.

    Note: This returns core questions only. For fungible questions,
    use get_fungible_questions() with the folder type.

    Args:
        language: The language key (e.g., 'python', 'typescript', 'go').

    Returns:
        List of Question instances to ask for this language.

    Raises:
        QuestionPipelineError: If a question class cannot be loaded.
        ValueError: If the language is not supported.
    """
    # For backward compatibility, return core questions
    return get_core_questions(language)
