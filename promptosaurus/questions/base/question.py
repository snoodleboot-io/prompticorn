"""Base question class for prompt init CLI.

This module defines the Question interface class that all question
implementations must inherit from. Each question represents a single
configuration choice in the prompt init flow.

Classes:
    Question: Interface class for all questions.
"""


class Question:
    """Base interface class for all questions in the prompt init flow.

    This interface class defines the interface that all question
    implementations must follow. Each question represents a single
    configuration choice that the user needs to make.

    Each question explains what it's solving and why, providing context
    to help users make informed decisions.

    Attributes:
        key: Unique identifier for this question.
        question_text: What to ask the user.
        explanation: Why we're asking - what problem it solves.
        options: Available options.
        option_explanations: Why each option exists (optional override).
        default: Sensible default choice.
        default_indices: Default selected indices for multi-select.
        allow_multiple: Whether multiple selections are allowed.
        none_index: Index of mutually exclusive option (optional).
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question.

        Returns:
            A unique string key that identifies this question.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement key property")

    @property
    def question_text(self) -> str:
        """What to ask the user.

        Returns:
            The question text to display to the user.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement question_text property"
        )

    @property
    def explanation(self) -> str:
        """Why we're asking this - what problem it solves.

        Returns:
            Explanation of why this question matters and what
            configuration problem it solves.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement explanation property")

    @property
    def options(self) -> list[str]:
        """Available options.

        Returns:
            List of option strings that the user can choose from.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement options property")

    @property
    def option_explanations(self) -> dict[str, str]:
        """Why each option exists. Override in subclasses.

        Returns:
            Dictionary mapping option strings to their explanations.
            Empty by default.
        """
        return {}

    @property
    def default(self) -> str:
        """Sensible default.

        Returns:
            The default option to use if user doesn't specify.
            Defaults to first option.
        """
        return self.options[0] if self.options else ""

    @property
    def default_indices(self) -> set[int]:
        """Default selected indices for multi-select questions. Override in subclasses.

        Returns:
            Set of default indices to select. Defaults to first option.
        """
        # Default to first option if no specific defaults set
        return {0} if self.options else set()

    @property
    def allow_multiple(self) -> bool:
        """Whether multiple selections are allowed. Default is False.

        Returns:
            True if multiple options can be selected, False otherwise.
        """
        return False

    def explain_option(self, option: str) -> str:
        """Get explanation for a specific option.

        Args:
            option: The option string to get explanation for.

        Returns:
            The explanation for the option, or empty string if not found.
        """
        return self.option_explanations.get(option, "")

    @property
    def none_index(self) -> int | None:
        """Index of option that is mutually exclusive with all others (e.g., 'none').

        If set, selecting this option deselects all others, and selecting any other
        option deselects this one. This is useful for questions like "Which
        frameworks do you use?" where "None" is an option.

        Returns:
            The index of the mutually exclusive option, or None if not applicable.
        """
        return None
