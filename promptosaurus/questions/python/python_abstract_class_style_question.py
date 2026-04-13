"""Question for selecting Python abstract class style."""

from promptosaurus.questions.base.question import Question


class PythonAbstractClassStyleQuestion(Question):
    """Question handler for Python abstract class style selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_abstract_class_style"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What abstract class style?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select your preferred style for defining abstract classes and interfaces."

    @property
    def options(self) -> list[str]:
        """Available styles."""
        return ["abc", "interface"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "interface"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "abc": "Python's ABC (Abstract Base Classes) module with NotImplementedError",
            "interface": "Protocol-based interfaces (more Pythonic, duck typing)",
        }
