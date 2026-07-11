"""PHP data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class PhpDataAccessQuestion(Question):
    """PHP data access / query layer - multi-select, backend-only.

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
        return ["Eloquent", "Doctrine ORM", "Laravel Query Builder", "PDO (raw SQL)"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "Eloquent": "Laravel's Active Record ORM",
            "Doctrine ORM": "Data Mapper ORM with a powerful DQL query language",
            "Laravel Query Builder": "Fluent SQL query builder without full ORM mapping",
            "PDO (raw SQL)": "Hand-written SQL via the PDO database abstraction",
        }

    @property
    def default(self) -> str:
        return "Eloquent"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Eloquent (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
