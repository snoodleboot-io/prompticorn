# Python mutation testing tool question

from promptosaurus.questions.base.question import Question


class PythonMutationToolQuestion(Question):
    """Question for Python mutation testing tool selection."""

    @property
    def key(self) -> str:
        return "mutation_tool"

    @property
    def question_text(self) -> str:
        return "What mutation testing tool do you want to use?"

    @property
    def explanation(self) -> str:
        return """Mutation testing evaluates test quality by introducing small changes (mutations) to code:
- mutmut: Most popular Python mutation tester, fast and comprehensive
- pytest-mutmut: pytest integration for mutmut, runs as pytest plugin
- none: Skip mutation testing (faster CI, less thorough)"""

    @property
    def options(self) -> list[str]:
        return ["mutmut", "pytest-mutmut", "none"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "mutmut": "Most popular - fast, comprehensive mutations, CLI-based (recommended)",
            "pytest-mutmut": "pytest plugin - runs as part of pytest, integrates with pytest ecosystem",
            "none": "Skip mutation testing - faster CI runs, less thorough test validation",
        }

    @property
    def default(self) -> str:
        return "mutmut"

    @property
    def none_index(self) -> int | None:
        # 'none' is at index 2
        return 2
