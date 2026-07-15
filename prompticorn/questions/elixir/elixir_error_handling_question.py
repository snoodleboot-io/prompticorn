"""Elixir error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class ElixirErrorHandlingQuestion(Question):
    """Elixir error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Elixir codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Elixir code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Tagged tuples", "with expressions", "raise / rescue"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Tagged tuples": "Return {:ok, value} / {:error, reason} tuples (idiomatic).",
            "with expressions": "Chain tagged-tuple results with with/1.",
            "raise / rescue": "Raise exceptions for truly exceptional cases.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
