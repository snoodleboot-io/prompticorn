# Terraform version question

from promptosaurus.questions.base.question import Question


class TerraformVersionQuestion(Question):
    """Question handler for Terraform version."""

    @property
    def key(self) -> str:
        return "terraform_version"

    @property
    def question_text(self) -> str:
        return "What Terraform version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Terraform version affects provider compatibility and language features.

- Newer versions have improved language features and bug fixes
- Terraform manages infrastructure as code across multiple providers
- Version affects available providers and module compatibility"""

    @property
    def options(self) -> list[str]:
        return ["1.7", "1.6", "1.5"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.7": "Latest stable - best features, recommended for new projects",
            "1.6": "Recent stable - excellent all-around",
            "1.5": "Stable - widely tested, maximum compatibility",
        }

    @property
    def default(self) -> str:
        return "1.7"
