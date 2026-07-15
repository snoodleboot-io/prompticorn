"""C# error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class CSharpErrorHandlingQuestion(Question):
    """C# error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the C# codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the C# code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions", "Result type", "Try-pattern"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Exceptions": "Throw and catch exceptions (idiomatic .NET default).",
            "Result type": "Return an explicit Result/Either value instead of throwing.",
            "Try-pattern": "Return bool with an out parameter (TryParse style).",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
