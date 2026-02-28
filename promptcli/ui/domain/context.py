"""Context models for UI pipeline."""

from pydantic import BaseModel


class QuestionContext(BaseModel):
    """Context for a question - passed through pipeline."""

    question: str
    options: list[str]
    explanations: dict[str, str]
    question_explanation: str
    default_index: int = 0
    allow_multiple: bool = False

    class Config:
        frozen = True


class PipelineContext:
    """Mutable context passed through pipeline stages."""

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
        """Get question context."""
        return self._question

    @property
    def state(self) -> "SelectionState":
        """Get current selection state."""
        return self._state

    @state.setter
    def state(self, value: "SelectionState") -> None:
        """Set selection state."""
        self._state = value

    @property
    def mode(self) -> str:
        """Get current mode (select or explain)."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Set current mode."""
        self._mode = value

    @property
    def display_options(self) -> list[str]:
        """Get options to display (includes Explain)."""
        opts = list(self._question.options)
        if "Explain" not in opts:
            opts.append("Explain")
        return opts

    def get_explanation(self, option: str) -> str:
        """Get explanation for option."""
        if option == "Explain":
            return "Learn more about this question"
        return self._question.explanations.get(option, "")


# Forward reference resolution
from promptcli.ui.state.single import SelectionState  # noqa: E402
