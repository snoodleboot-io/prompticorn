"""Rust error-handling pattern question (core, per-language)."""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class RustErrorHandlingQuestion(Question):
    """Rust error-handling pattern - core (asked once per language).

    Documents how errors are surfaced and handled across the Rust codebase
    so agents follow a consistent, language-idiomatic approach. Stored on the spec.
    """

    @property
    def key(self) -> str:
        return "error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does the Rust code follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Result and ? operator", "Panic", "Boxed error trait"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            NOT_SPECIFIED: "Leave unset - renders a clear placeholder in the conventions.",
            "Result and ? operator": "Return Result<T, E> and propagate with the ? operator (idiomatic).",
            "Panic": "panic! for unrecoverable bugs, not for expected errors.",
            "Boxed error trait": "Return Box<dyn std::error::Error> for heterogeneous errors.",
        }

    @property
    def default(self) -> str:
        return NOT_SPECIFIED
