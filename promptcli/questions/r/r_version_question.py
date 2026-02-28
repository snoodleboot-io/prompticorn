# R version question

from promptcli.questions.base.question import Question


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
        return ["4.3", "4.2", "4.1"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "4.3": "Latest stable - best features, recommended for new projects",
            "4.2": "Recent stable - excellent all-around",
            "4.1": "Long-term support - maximum package compatibility",
        }

    @property
    def default(self) -> str:
        return "4.3"
