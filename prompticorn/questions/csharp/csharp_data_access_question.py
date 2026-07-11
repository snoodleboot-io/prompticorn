"""C# data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class CSharpDataAccessQuestion(Question):
    """C# data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers ORMs,
    micro-ORMs, and raw SQL. A folder may combine several, so multiple
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
            "The layer agents use to read and write data - ORMs, micro-ORMs, or raw SQL. "
            "Documented in the core conventions. Select all that apply."
        )

    @property
    def options(self) -> list[str]:
        return ["Entity Framework Core", "Dapper", "NHibernate", "ADO.NET (raw SQL)"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "Entity Framework Core": "Microsoft's full-featured ORM with LINQ and migrations",
            "Dapper": "High-performance micro-ORM mapping SQL results to objects",
            "NHibernate": "Mature, configurable ORM ported from Hibernate",
            "ADO.NET (raw SQL)": "Hand-written SQL via the ADO.NET data provider APIs",
        }

    @property
    def default(self) -> str:
        return "Entity Framework Core"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Entity Framework Core (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
