"""TypeScript error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class TypeScriptErrorHandlingQuestion(Question):
    """TypeScript error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the TypeScript codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the
    spec. Reused for JavaScript per the existing TypeScript* reuse pattern.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the TypeScript code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions", "Result type", "Error values / codes"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Exceptions": "Throw and catch errors (idiomatic TypeScript default).",
            "Result type": "Return an explicit Result/Either value instead of throwing.",
            "Error values / codes": "Return error values or status codes from functions.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
