# Base question class for prompt init CLI

from abc import ABC, abstractmethod


class Question(ABC):
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

    @property
    def allow_multiple(self) -> bool:
        """Whether multiple selections are allowed. Default is False."""
        return False

    def explain_option(self, option: str) -> str:
        """Get explanation for a specific option."""
        return self.option_explanations.get(option, "")
