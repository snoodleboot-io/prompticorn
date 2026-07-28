"""Question for selecting the C language standard (PRO-136)."""

from prompticorn.questions.base.question import Question


class CVersionQuestion(Question):
    """Question handler for C standard selection."""

    @property
    def key(self) -> str:
        return "c_version"

    @property
    def question_text(self) -> str:
        return "What C standard?"

    @property
    def explanation(self) -> str:
        return "Select the C language standard your project targets."

    @property
    def options(self) -> list[str]:
        return ["C23", "C17", "C11", "C99"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "C23": "C23 - Latest standard (typeof, constexpr, #embed)",
            "C17": "C17 - Bugfix revision of C11; widely supported default",
            "C11": "C11 - Atomics, _Generic, threads",
            "C99": "C99 - Older baseline for maximum portability",
        }

    @property
    def default(self) -> str:
        return "C23"

    config_key = "runtime"
