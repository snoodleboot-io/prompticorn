"""Python source-tree layout style question (core, per-language)."""

from prompticorn.questions.base.question import Question


class PythonLayoutStyleQuestion(Question):
    """Python source-tree layout style (flat vs src) - core, per-language.

    Drives the source layout block rendered in the core conventions. Stored on
    the spec so each language carries its own layout choice.
    """

    @property
    def key(self) -> str:
        return "layout_style"

    @property
    def question_text(self) -> str:
        return "Which source-tree layout should the Python conventions document?"

    @property
    def explanation(self) -> str:
        return (
            "flat: package/modules at the repo root (idiomatic default).\n"
            "src: sources nested under a src/ directory."
        )

    @property
    def options(self) -> list[str]:
        return ["flat", "src"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "flat": "Package/modules at the repo root (recommended default).",
            "src": "Sources nested under a src/ directory.",
        }

    @property
    def default(self) -> str:
        return "flat"
