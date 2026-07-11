"""F# data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class FSharpDataAccessQuestion(Question):
    """F# data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers type
    providers, ORMs, and raw SQL. A folder may combine several, so multiple
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
            "The layer agents use to read and write data - type providers, ORMs, or raw "
            "SQL. Documented in the core conventions. Select all that apply."
        )

    @property
    def options(self) -> list[str]:
        return ["SQLProvider", "Dapper.FSharp", "Entity Framework Core", "ADO.NET (raw SQL)"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "SQLProvider": "Type provider giving compile-time access to the database schema",
            "Dapper.FSharp": "Idiomatic F# wrapper over the Dapper micro-ORM",
            "Entity Framework Core": "Microsoft's full-featured ORM usable from F#",
            "ADO.NET (raw SQL)": "Hand-written SQL via the ADO.NET data provider APIs",
        }

    @property
    def default(self) -> str:
        return "Dapper.FSharp"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Dapper.FSharp (1)."""
        return {1}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
