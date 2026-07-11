"""Scala data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class ScalaDataAccessQuestion(Question):
    """Scala data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers ORMs,
    functional query libraries, and raw SQL. A folder may combine several, so
    multiple selections are allowed.
    """

    @property
    def key(self) -> str:
        return "data_access"

    @property
    def question_text(self) -> str:
        return "Which data access / query layer(s) does this folder use?"

    @property
    def explanation(self) -> str:
        return (
            "The layer agents use to read and write data - ORMs, functional query "
            "libraries, or raw SQL. Documented in the core conventions. Select all that "
            "apply."
        )

    @property
    def options(self) -> list[str]:
        return ["Slick", "Doobie", "Quill", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "Slick": "Functional-relational mapping with a collection-like query API",
            "Doobie": "Pure functional JDBC layer for the Cats ecosystem",
            "Quill": "Compile-time quoted DSL generating SQL from Scala code",
            "Raw SQL": "Hand-written SQL via JDBC or a thin helper",
        }

    @property
    def default(self) -> str:
        return "Doobie"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Doobie (1)."""
        return {1}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
