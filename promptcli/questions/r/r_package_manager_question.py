# R package manager question

from promptcli.questions.base.question import Question


class RPackageManagerQuestion(Question):
    """Question handler for R package manager."""

    @property
    def key(self) -> str:
        return "r_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for R?"

    @property
    def explanation(self) -> str:
        return """Package managers handle R dependencies and environment reproducibility.

- renv is the modern approach for project-specific environments
- Packrat provides similar functionality with a different approach
- renv is recommended for new projects"""

    @property
    def options(self) -> list[str]:
        return ["renv", "packrat"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "renv": "Modern project environments - fast, reliable, recommended",
            "packrat": "Legacy environment management - widely used",
        }

    @property
    def default(self) -> str:
        return "renv"
