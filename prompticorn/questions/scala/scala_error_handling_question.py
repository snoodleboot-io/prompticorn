"""Scala error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class ScalaErrorHandlingQuestion(Question):
    """Scala error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Scala codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Scala code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Either / Try", "Option", "Exceptions"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Either / Try": "Return Either or Try to model failures functionally (idiomatic).",
            "Option": "Return Option for absence; None on failure.",
            "Exceptions": "Throw and catch exceptions.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
