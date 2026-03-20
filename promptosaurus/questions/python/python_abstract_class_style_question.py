# Python abstract class style question

from promptosaurus.questions.base.question import Question


class PythonAbstractClassStyleQuestion(Question):
    """Question for Python abstract class implementation style."""

    @property
    def key(self) -> str:
        return "python_abstract_class_style"

    @property
    def question_text(self) -> str:
        return "How should abstract classes/interfaces be implemented?"

    @property
    def options(self) -> list[str]:
        return ["abc", "interface"]

    @property
    def explanation(self) -> str:
        return """Abstract class style affects how you define interfaces and abstract base classes:
- abc: Formal abstract base classes using the abc module (explicit, type-checker friendly)
- interface: Informal interfaces using NotImplementedError (simpler, duck-typing friendly)"""

    @property
    def default(self) -> str:
        return "interface"

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "abc": "Formal abstract base classes using the abc module (explicit, type-checker friendly)",
            "interface": "Informal interfaces using NotImplementedError (simpler, duck-typing friendly)",
        }
