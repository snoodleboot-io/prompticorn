# Language registry and factory functions

from pathlib import Path

import yaml
from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.sweet_tea_error import SweetTeaError

from promptcli.questions.base import Question


class QuestionPipelineError(Exception):
    """Raised when a question cannot be loaded from the pipeline."""

    def __init__(self, class_name: str, language: str, reason: str) -> None:
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
]


def _load_pipelines() -> dict[str, list[str]]:
    """Load question pipelines from YAML file."""
    pipelines_path = Path(__file__).parent / "question_pipelines.yaml"
    with open(pipelines_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_language_questions(language: str) -> list[Question]:
    """
    Get all questions for a specific language.

    Returns a list of questions that should be asked for the given language.
    """
    questions: list[Question] = []
    lang = language.lower()

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
