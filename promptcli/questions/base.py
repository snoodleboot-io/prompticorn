# Base question classes for prompt init CLI

from abc import ABC, abstractmethod


class BaseQuestion(ABC):
    """
    Base class for all questions in the prompt init flow.

    Each question explains what it's solving and why.
    """

    @property
    @abstractmethod
    def key(self) -> str:
        """Unique identifier for this question."""
        pass

    @property
    @abstractmethod
    def question_text(self) -> str:
        """What to ask the user."""
        pass

    @property
    @abstractmethod
    def explanation(self) -> str:
        """Why we're asking this - what problem it solves."""
        pass

    @property
    @abstractmethod
    def options(self) -> list[str]:
        """Available options."""
        pass

    @property
    def option_explanations(self) -> dict[str, str]:
        """Why each option exists. Override in subclasses."""
        return {}

    @property
    def default(self) -> str:
        """Sensible default."""
        return self.options[0] if self.options else ""

    def explain_option(self, option: str) -> str:
        """Get explanation for a specific option."""
        return self.option_explanations.get(option, "")


class RepositoryTypeQuestion(BaseQuestion):
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


class FolderMappingQuestion(BaseQuestion):
    """Question about folder to language mappings."""

    def __init__(self, num_folders: int = 1):
        self._num_folders = num_folders

    @property
    def key(self) -> str:
        return "folder_mapping"

    @property
    def question_text(self) -> str:
        return "Enter folder paths and their languages (one per line)"

    @property
    def explanation(self) -> str:
        return """Map each folder to its primary language.

Example:
  /frontend → typescript
  /backend → python
  /shared → go

This determines which language conventions to apply for each area."""

    @property
    def options(self) -> list[str]:
        return []  # Dynamic - depends on number of folders

    @property
    def default(self) -> str:
        return ""


# Repository type enum for type safety
REPO_TYPE_SINGLE = "single-language"
REPO_TYPE_MULTI_FOLDER = "multi-language-folder"
REPO_TYPE_MIXED = "mixed"

REPO_TYPES = [REPO_TYPE_SINGLE, REPO_TYPE_MULTI_FOLDER, REPO_TYPE_MIXED]
