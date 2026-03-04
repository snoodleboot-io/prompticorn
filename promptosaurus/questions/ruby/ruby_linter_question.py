# Ruby linter question

from promptosaurus.questions.base.question import Question


class RubyLinterQuestion(Question):
    """Question for Ruby linter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "ruby_linter"

    @property
    def question_text(self) -> str:
        return "What linter(s) do you want to use for Ruby?"

    @property
    def explanation(self) -> str:
        return """Linters check code quality, style, and potential bugs. You can select multiple:
- RuboCop: The most popular Ruby linter, highly configurable
- Standard: A simpler, no-configuration alternative to RuboCop"""

    @property
    def options(self) -> list[str]:
        return ["rubocop", "standard"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "rubocop": "Most popular - highly configurable, extensive rules, recommended",
            "standard": "Zero-config - simpler, no decisions needed, community driven",
        }

    @property
    def default(self) -> str:
        return "rubocop"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple linters."""
        return True
