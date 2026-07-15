"""PHP error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class PhpErrorHandlingQuestion(Question):
    """PHP error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the PHP codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the PHP code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions", "Result objects", "Error return values"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Exceptions": "Throw and catch exceptions (idiomatic PHP default).",
            "Result objects": "Return result objects instead of throwing.",
            "Error return values": "Return error values or codes from functions.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
