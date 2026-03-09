"""Language registry and factory functions.

This module provides the language question loading infrastructure for promptosaurus.
It handles loading question pipelines from YAML configuration and instantiating
the appropriate Question classes using the sweet_tea factory pattern.

Functions:
    get_language_questions: Get all questions for a specific language.
    _load_pipelines: Load question pipelines from YAML file.

Classes:
    QuestionPipelineError: Exception raised when a question cannot be loaded.

Constants:
    LANGUAGE_KEYS: List of available language keys for dynamic lookup.

Example:
    >>> from promptosaurus.questions.language import get_language_questions, LANGUAGE_KEYS
    >>>
    >>> # Check available languages
    >>> print("python" in LANGUAGE_KEYS)
    True
    >>>
    >>> # Get questions for Python
    >>> questions = get_language_questions("python")
    >>> print(f\"Found {len(questions)} questions for Python\")
    >>> for q in questions[:3]:
    ...     print(f\"  - {q.key}: {q.question_text}\")
"""

from pathlib import Path

import yaml  # type: ignore[import-untyped]
from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.sweet_tea_error import SweetTeaError

from promptosaurus.questions.base.question import Question


class QuestionPipelineError(Exception):
    """Raised when a question cannot be loaded from the pipeline.

    This exception is raised when the question pipeline configuration
    references a question class that cannot be loaded or instantiated.

    Attributes:
        class_name: The name of the question class that failed to load.
        language: The language for which the question was being loaded.
        reason: The reason for the failure.

    Example:
        >>> try:
        ...     questions = get_language_questions("invalid_language")
        ... except QuestionPipelineError as e:
        ...     print(e.class_name)
        ...     print(e.language)
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
LANGUAGE_KEYS = [
    "python",
    "typescript",
    "javascript",
    "java",
    "csharp",
    "go",
    "rust",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "elixir",
    "elm",
    "haskell",
    "clojure",
    "fsharp",
    "dart",
    "julia",
    "lua",
    "r",
    "shell",
    "groovy",
    "terraform",
    "sql",
    "html",
]


def _load_pipelines() -> dict[str, list[str]]:
    """Load question pipelines from YAML file.

    Reads the question_pipelines.yaml file which defines which
    question classes should be asked for each language.

    Returns:
        Dictionary mapping language keys to lists of question class names.

    Raises:
        FileNotFoundError: If the pipelines YAML file doesn't exist.
        yaml.YAMLError: If the YAML file is malformed.

    Example:
        >>> pipelines = _load_pipelines()
        >>> print(pipelines.get("python", []))
        ['LanguageQuestion', 'PythonLinterQuestion', ...]
    """
    pipelines_path = Path(__file__).parent / "question_pipelines.yaml"
    with open(pipelines_path, encoding="utf-8") as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]


def get_language_questions(language: str) -> list[Question]:
    """Get all questions for a specific language.

    Loads and instantiates all Question classes defined in the pipeline
    for the given language using the sweet_tea AbstractFactory.

    Args:
        language: The language key (e.g., 'python', 'typescript', 'go').

    Returns:
        List of Question instances to ask for this language.

    Raises:
        QuestionPipelineError: If a question class cannot be loaded.
        ValueError: If the language is not supported.

    Example:
        >>> questions = get_language_questions("python")
        >>> print(f\"Found {len(questions)} questions\")
        >>> for q in questions:
        ...     print(f\"  {q.key}: {q.question_text}\")
    """
    questions: list[Question] = []
    lang = language.lower()

    # Validate language is supported
    if lang not in LANGUAGE_KEYS:
        raise ValueError(f"Unsupported language: {lang}. Available: {LANGUAGE_KEYS}")

    # Load pipeline from YAML
    pipelines = _load_pipelines()
    question_classes = pipelines.get(lang, [])

    # Instantiate each question class using sweet_tea AbstractFactory
    factory = AbstractFactory[Question]
    for class_name in question_classes:
        try:
            question = factory.create(class_name)
            questions.append(question)
        except SweetTeaError as e:
            # Class not found in registry or type mismatch
            raise QuestionPipelineError(
                class_name=class_name,
                language=lang,
                reason=f"Class not registered or not a subclass of BaseQuestion: {e}",
            ) from e

    return questions
