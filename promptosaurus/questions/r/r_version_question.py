# R version question

from promptosaurus.questions.base.question import Question


class RVersionQuestion(Question):
    """Question handler for R version."""

    @property
    def key(self) -> str:
        return "r_version"

    @property
    def question_text(self) -> str:
        return "What R version do you want to use?"

    @property
    def explanation(self) -> str:
        return """R version affects statistical computing capabilities and package availability.

- Newer versions have improved performance and features
- R is widely used for statistical analysis and data science
- Version affects CRAN package compatibility"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["4.3", "4.2", "4.1", "4.0"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "4.3"

    config_key = "runtime"
