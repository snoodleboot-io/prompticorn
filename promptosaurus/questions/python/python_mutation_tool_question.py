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
