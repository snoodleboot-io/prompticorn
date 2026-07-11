"""TypeScript data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class TypeScriptDataAccessQuestion(Question):
    """TypeScript data access / query layer - multi-select, backend-only.

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
        return ["Prisma", "TypeORM", "Drizzle", "Sequelize", "Kysely", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "Prisma": "Schema-first ORM with generated, type-safe client and migrations",
            "TypeORM": "Decorator-based ORM supporting Active Record and Data Mapper patterns",
            "Drizzle": "Lightweight, type-safe SQL query builder and ORM",
            "Sequelize": "Mature promise-based ORM for SQL databases",
            "Kysely": "Type-safe SQL query builder with no runtime ORM overhead",
            "Raw SQL": "Hand-written SQL via a database driver or thin helper",
        }

    @property
    def default(self) -> str:
        return "Prisma"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Prisma (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
