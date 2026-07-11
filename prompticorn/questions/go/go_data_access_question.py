"""Go data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class GoDataAccessQuestion(Question):
    """Go data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers ORMs,
    code generators, and raw SQL. A folder may combine several, so multiple
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
            "The layer agents use to read and write data - ORMs, code generators, or raw "
            "SQL. Documented in the core conventions. Select all that apply."
        )

    @property
    def options(self) -> list[str]:
        return ["GORM", "sqlc", "Ent", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "GORM": "Full-featured ORM with associations, hooks, and migrations",
            "sqlc": "Generates type-safe Go from hand-written SQL queries",
            "Ent": "Entity framework with a typed, code-generated graph API",
            "Raw SQL": "Hand-written SQL via database/sql or a thin helper",
        }

    @property
    def default(self) -> str:
        return "sqlc"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: sqlc (1)."""
        return {1}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
