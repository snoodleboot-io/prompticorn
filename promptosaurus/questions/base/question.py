"""Base question class for prompt init CLI.

This module defines the Question abstract base class that all question
implementations must inherit from. Each question represents a single
configuration choice in the prompt init flow.

Classes:
    Question: Abstract base class for all questions.

Example:
    >>> from promptosaurus.questions.base.question import Question
    >>>
    >>> # Each question must implement these properties:
    >>> # - key: Unique identifier
    >>> # - question_text: What to ask
    >>> # - explanation: Why we're asking
    >>> # - options: Available choices
"""

from abc import ABC, abstractmethod


class Question(ABC):
    """Base class for all questions in the prompt init flow.

    This abstract base class defines the interface that all question
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

    Example:
        >>> class MyQuestion(Question):
        ...     @property
        ...     def key(self) -> str:
        ...         return "my_question"
        ...
        ...     @property
        ...     def question_text(self) -> str:
        ...         return "Choose an option:"
        ...
        ...     @property
        ...     def explanation(self) -> str:
        ...         return "This helps with X"
        ...
        ...     @property
        ...     def options(self) -> list[str]:
        ...         return ["A", "B", "C"]
    """

    @property
    @abstractmethod
    def key(self) -> str:
        """Unique identifier for this question.

        Returns:
            A unique string key that identifies this question.

        Example:
            >>> class MyQuestion(Question):
            ...     @property
            ...     def key(self) -> str:
            ...         return "language"
        """
        pass

    @property
    @abstractmethod
    def question_text(self) -> str:
        """What to ask the user.

        Returns:
            The question text to display to the user.

        Example:
            >>> class MyQuestion(Question):
            ...     @property
            ...     def question_text(self) -> str:
            ...         return "Choose your programming language:"
        """
        pass

    @property
    @abstractmethod
    def explanation(self) -> str:
        """Why we're asking this - what problem it solves.

        Returns:
            Explanation of why this question matters and what
            configuration problem it solves.

        Example:
            >>> class MyQuestion(Question):
            ...     @property
            ...     def explanation(self) -> str:
            ...         return "The language determines available tools and conventions"
        """
        pass

    @property
    @abstractmethod
    def options(self) -> list[str]:
        """Available options.

        Returns:
            List of option strings that the user can choose from.

        Example:
            >>> class MyQuestion(Question):
            ...     @property
            ...     def options(self) -> list[str]:
            ...         return ["Python", "TypeScript", "Go"]
        """
        pass

    @property
    def option_explanations(self) -> dict[str, str]:
        """Why each option exists. Override in subclasses.

        Returns:
            Dictionary mapping option strings to their explanations.
            Empty by default.

        Example:
            >>> class MyQuestion(Question):
            ...     @property
            ...     def option_explanations(self) -> dict[str, str]:
            ...         return {
            ...             "Python": "Great for data science",
            ...             "TypeScript": "Type-safe JavaScript"
            ...         }
        """
        return {}

    @property
    def default(self) -> str:
        """Sensible default.

        Returns:
            The default option to use if user doesn't specify.
            Defaults to first option.

        Example:
            >>> question = MyQuestion()
            >>> print(question.default)
            Python
        """
        return self.options[0] if self.options else ""

    @property
    def default_indices(self) -> set[int]:
        """Default selected indices for multi-select questions. Override in subclasses.

        Returns:
            Set of default indices to select. Defaults to first option.

        Example:
            >>> question = MyQuestion()
            >>> print(question.default_indices)
            {0}
        """
        # Default to first option if no specific defaults set
        return {0} if self.options else set()

    @property
    def allow_multiple(self) -> bool:
        """Whether multiple selections are allowed. Default is False.

        Returns:
            True if multiple options can be selected, False otherwise.

        Example:
            >>> question = MyQuestion()
            >>> print(question.allow_multiple)
            False
        """
        return False

    def explain_option(self, option: str) -> str:
        """Get explanation for a specific option.

        Args:
            option: The option string to get explanation for.

        Returns:
            The explanation for the option, or empty string if not found.

        Example:
            >>> question = MyQuestion()
            >>> print(question.explain_option("Python"))
            Great for data science
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

        Example:
            >>> class FrameworkQuestion(Question):
            ...     @property
            ...     def none_index(self) -> int | None:
            ...         return 0  # "None" is first option
        """
        return None
