"""Context models for UI pipeline.

This module provides the context models that are passed through the UI pipeline.
These models hold the immutable question data and mutable pipeline state.

Classes:
    QuestionContext: Immutable context for a question (Pydantic model).
    PipelineContext: Mutable context passed through pipeline stages.
"""

from pydantic import BaseModel


class QuestionContext(BaseModel):
    """Context for a question - passed through pipeline.

    This Pydantic model holds all the immutable data about a question,
    including the question text, available options, explanations, and
    default selections.

    Attributes:
        question: The main question/prompt text.
        options: List of available options to choose from.
        explanations: Dictionary mapping options to their explanations.
        question_explanation: Detailed explanation of what the question means.
        default_index: Index of the default option.
        default_indices: Set of default indices for multi-select.
        allow_multiple: Whether multiple selections are allowed.
        none_index: Index for a mutually exclusive option (e.g., "none of the above").

    Config:
        frozen: True - instances are immutable after creation.
    """

    question: str
    options: list[str]
    explanations: dict[str, str]
    question_explanation: str
    default_index: int = 0
    default_indices: set[int] = {0}
    allow_multiple: bool = False
    none_index: int | None = None  # Index of option that is mutually exclusive (e.g., 'none')

    class Config:
        frozen = True


class PipelineContext:
    """Mutable context passed through pipeline stages.

    This class holds the mutable state during pipeline execution,
    including the current selection state and display mode. It wraps
    the immutable QuestionContext and adds mutable properties.

    Attributes:
        _question: The immutable question context.
        _state: Current selection state.
        _mode: Current display mode (select or explain).

    Properties:
        question: Returns the QuestionContext.
        state: Get/set the current SelectionState.
        mode: Get/set the current mode (select or explain).
        display_options: Get options to display.
    """

    def __init__(
        self,
        question: QuestionContext,
        state: "SelectionState",
        mode: str = "select",
    ):
        self._question = question
        self._state = state
        self._mode = mode

    @property
    def question(self) -> QuestionContext:
        """Get question context.

        Returns:
            The immutable QuestionContext for this pipeline.
        """
        return self._question

    @property
    def state(self) -> "SelectionState":
        """Get current selection state.

        Returns:
            The current SelectionState instance.
        """
        return self._state

    @state.setter
    def state(self, value: "SelectionState") -> None:
        """Set selection state.

        Args:
            value: New SelectionState instance to set.
        """
        self._state = value

    @property
    def mode(self) -> str:
        """Get current mode (select or explain).

        Returns:
            The current mode string ('select' or 'explain').
        """
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Set current mode.

        Args:
            value: New mode string ('select' or 'explain').
        """
        self._mode = value

    @property
    def display_options(self) -> list[str]:
        """Get options to display (without Explain - use 'e' keystroke instead).

        Returns:
            List of option strings to display to the user.
        """
        return list(self._question.options)

    def get_explanation(self, option: str) -> str:
        """Get explanation for option.

        Args:
            option: The option string to get explanation for.

        Returns:
            The explanation string, or empty string if not found.
        """
        if option == "Explain":
            return "Learn more about this question"
        return self._question.explanations.get(option, "")


# Forward reference resolution
from promptosaurus.ui.state.selection_state import SelectionState  # noqa: E402
