# Question handlers for different repository types

from typing import Any


class LanguageQuestionHandler:
    """
    Base class for handling language-specific questions.

    This class defines the interface for question handlers.
    Subclasses should implement the handle() method to provide
    specific behavior for different repository types.
    """

    def handle(self, repo_type: str) -> dict[str, Any]:
        """
        Handle questions for the given repository type.

        Args:
            repo_type: The repository type string

        Returns:
            Configuration dictionary with user responses
        """
        raise NotImplementedError("Subclasses must implement handle()")
