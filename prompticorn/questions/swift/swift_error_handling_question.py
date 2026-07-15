"""Swift error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class SwiftErrorHandlingQuestion(Question):
    """Swift error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Swift codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Swift code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "throws / try", "Result type", "Optionals"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "throws / try": "Mark functions throws and handle with do/try/catch (idiomatic).",
            "Result type": "Return Result<Success, Failure> instead of throwing.",
            "Optionals": "Return optionals and handle nil at the call site.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
