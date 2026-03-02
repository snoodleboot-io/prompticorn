# Python abstract class style question

from promptcli.questions.base.question import Question


class PythonAbstractClassStyleQuestion(Question):
    """Question for Python abstract class implementation style."""

    @property
    def key(self) -> str:
        return "python_abstract_class_style"

    @property
    def question_text(self) -> str:
        return "How should abstract classes/interfaces be implemented?"

    @property
    def explanation(self) -> str:
        return """Abstract class style affects how you define interfaces and abstract base classes:
- abc: Formal abstract base classes using the abc module (explicit, type-checker friendly)
- interface: Informal interfaces using NotImplementedError (simpler, duck-typing friendly)"""

    @property
    def options(self) -> list[str]:
        return ["abc", "interface"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "abc": "Abstract Base Classes - use abc.ABC and @abstractmethod for formal interfaces",
            "interface": "NotImplementedError - raise in methods to indicate subclass must override",
        }

    @property
    def default(self) -> str:
        return "abc"
