"""Question for selecting the C++ language standard (PRO-136)."""

from prompticorn.questions.base.question import Question


class CppVersionQuestion(Question):
    """Question handler for C++ standard selection."""

    @property
    def key(self) -> str:
        return "cpp_version"

    @property
    def question_text(self) -> str:
        return "What C++ standard?"

    @property
    def explanation(self) -> str:
        return "Select the C++ language standard your project targets."

    @property
    def options(self) -> list[str]:
        return ["C++23", "C++20", "C++17", "C++14", "C++11"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "C++23": "C++23 - Latest standard (std::expected, ranges improvements)",
            "C++20": "C++20 - Concepts, ranges, coroutines, modules",
            "C++17": "C++17 - Structured bindings, std::optional; strong default",
            "C++14": "C++14 - Incremental improvements over C++11",
            "C++11": "C++11 - Move semantics, lambdas, smart pointers baseline",
        }

    @property
    def default(self) -> str:
        return "C++23"

    config_key = "runtime"
