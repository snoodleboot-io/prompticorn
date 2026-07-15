"""Kotlin error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class KotlinErrorHandlingQuestion(Question):
    """Kotlin error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Kotlin codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Kotlin code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions", "Result type", "Sealed class results"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Exceptions": "Throw and catch exceptions (idiomatic Kotlin/JVM default).",
            "Result type": "Return kotlin.Result instead of throwing.",
            "Sealed class results": "Model outcomes with a sealed class hierarchy.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
