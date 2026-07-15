"""F# error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class FSharpErrorHandlingQuestion(Question):
    """F# error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the F# codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the F# code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Result type", "Option type", "Exceptions"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Result type": "Return Result<'T, 'TError> and compose with the Result module (idiomatic).",
            "Option type": "Return Option for absence.",
            "Exceptions": "Throw and catch .NET exceptions.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
