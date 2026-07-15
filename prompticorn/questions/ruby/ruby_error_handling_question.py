"""Ruby error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class RubyErrorHandlingQuestion(Question):
    """Ruby error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Ruby codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Ruby code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions (raise/rescue)", "Result objects", "nil returns"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Exceptions (raise/rescue)": "Raise and rescue exceptions (idiomatic Ruby default).",
            "Result objects": "Return result objects instead of raising.",
            "nil returns": "Return nil on failure and check at the call site.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
