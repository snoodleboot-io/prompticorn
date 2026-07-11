"""Go source-tree layout style question (core, per-language)."""

from prompticorn.questions.base.question import Question


class GoLayoutStyleQuestion(Question):
    """Go source-tree layout style (flat vs src) - core, per-language.

    Drives the source layout block rendered in the core conventions. Stored on
    the spec. Go favours a flat module layout with cmd/ and internal/ packages.
    """

    @property
    def key(self) -> str:
        return "layout_style"

    @property
    def question_text(self) -> str:
        return "Which source-tree layout should the Go conventions document?"

    @property
    def explanation(self) -> str:
        return (
            "flat: packages at the module root with cmd/ and internal/ (idiomatic default).\n"
            "src: sources nested under a src/ directory."
        )

    @property
    def options(self) -> list[str]:
        return ["flat", "src"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "flat": "Packages at the module root with cmd/ and internal/ (recommended).",
            "src": "Sources nested under a src/ directory.",
        }

    @property
    def default(self) -> str:
        return "flat"
