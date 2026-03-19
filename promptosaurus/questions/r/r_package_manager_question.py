# R package manager question

from promptosaurus.questions.base.question import Question


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
