"""Elixir data access / query layer question for backend folders."""

from prompticorn.questions.base.question import Question


class ElixirDataAccessQuestion(Question):
    """Elixir data access / query layer - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. Covers Ecto
    and raw SQL. A folder may combine several, so multiple selections are
    allowed.
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
            "The layer agents use to read and write data - Ecto or raw SQL. Documented in "
            "the core conventions. Select all that apply."
        )

    @property
    def options(self) -> list[str]:
        return ["Ecto", "Raw SQL"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "Ecto": "Elixir's database wrapper and composable query DSL",
            "Raw SQL": "Hand-written SQL via Ecto.Adapters.SQL or a driver",
        }

    @property
    def default(self) -> str:
        return "Ecto"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: Ecto (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several data access layers."""
        return True
