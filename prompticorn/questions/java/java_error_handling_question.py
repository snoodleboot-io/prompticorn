"""Java error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class JavaErrorHandlingQuestion(Question):
    """Java error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Java codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Java code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Checked exceptions", "Unchecked exceptions", "Optional / Result"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Checked exceptions": "Declare and handle checked exceptions on the method signature.",
            "Unchecked exceptions": "Throw runtime (unchecked) exceptions.",
            "Optional / Result": "Return Optional or a Result type instead of throwing.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
