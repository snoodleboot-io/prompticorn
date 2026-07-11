"""Java data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class JavaDataAccessQuestion(Question):
    """Java data access / query layer - multi-select, backend-only.

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
        return ["JPA / Hibernate", "Spring Data JPA", "jOOQ", "MyBatis", "JDBC (raw SQL)"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "JPA / Hibernate": "Standard JPA persistence backed by the Hibernate ORM",
            "Spring Data JPA": "Repository abstraction over JPA for Spring applications",
            "jOOQ": "Type-safe SQL query builder generated from the schema",
            "MyBatis": "SQL mapper coupling Java methods to hand-written SQL",
            "JDBC (raw SQL)": "Hand-written SQL via the JDBC API",
        }

    @property
    def default(self) -> str:
        return "Spring Data JPA"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Spring Data JPA (1)."""
        return {1}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
