"""Python error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class PythonErrorHandlingQuestion(Question):
    """Python error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Python codebase so
    agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Python code follow?"

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
            "Exceptions": "Raise and catch exceptions (idiomatic Python default).",
            "Result type": "Return an explicit Result/Either value instead of raising.",
            "Error values / codes": "Return error values or status codes from functions.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
