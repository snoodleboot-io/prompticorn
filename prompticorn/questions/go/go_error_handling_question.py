"""Go error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class GoErrorHandlingQuestion(Question):
    """Go error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Go codebase so
    agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Go code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Error values (idiomatic)", "Wrapped errors", "Panic / recover"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Error values (idiomatic)": "Return error as the last value and check it (Go default).",
            "Wrapped errors": "Wrap errors with fmt.Errorf %w and inspect via errors.Is/As.",
            "Panic / recover": "Use panic/recover for truly exceptional, unrecoverable cases.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
