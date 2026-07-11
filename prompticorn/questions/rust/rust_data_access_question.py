"""Rust data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class RustDataAccessQuestion(Question):
    """Rust data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers ORMs,
    query builders, and raw SQL. A folder may combine several, so multiple
    selections are allowed.
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
        return ["SQLx", "Diesel", "SeaORM", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "SQLx": "Async, compile-time checked SQL toolkit without an ORM",
            "Diesel": "Type-safe ORM and query builder with a strong macro DSL",
            "SeaORM": "Async, dynamic ORM built on top of SQLx",
            "Raw SQL": "Hand-written SQL via a database driver or thin helper",
        }

    @property
    def default(self) -> str:
        return "SQLx"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: SQLx (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
