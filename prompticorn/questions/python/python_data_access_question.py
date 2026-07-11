"""Python data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class PythonDataAccessQuestion(Question):
    """Python data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers ORMs,
    query builders, and raw SQL. A folder may combine several (e.g. SQLAlchemy
    plus Raw SQL for hot paths), so multiple selections are allowed.
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
            "The layer agents use to read and write data - ORMs, query builders, or raw "
            "SQL. Documented in the core conventions. Select all that apply."
        )

    @property
    def options(self) -> list[str]:
        return ["SQLAlchemy", "Django ORM", "Tortoise ORM", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "SQLAlchemy": "Mature ORM and Core query builder with sync and async support",
            "Django ORM": "Batteries-included ORM bundled with the Django framework",
            "Tortoise ORM": "Async-native ORM inspired by the Django ORM",
            "Raw SQL": "Hand-written SQL via DB-API drivers or a thin helper",
        }

    @property
    def default(self) -> str:
        return "SQLAlchemy"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: SQLAlchemy (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
