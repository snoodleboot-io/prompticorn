# Julia package manager question

from promptosaurus.questions.base.question import Question


class JuliaPackageManagerQuestion(Question):
    """Question handler for Julia package manager."""

    @property
    def key(self) -> str:
        return "julia_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for Julia?"

    @property
    def explanation(self) -> str:
        return """Julia's package manager handles dependencies and project environments.

- Pkg is the built-in package manager for Julia
- It uses project-specific environments for reproducibility
- No additional tools needed as Pkg is included with Julia"""

    @property
    def options(self) -> list[str]:
        return ["pkg"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "pkg": "Julia's built-in package manager - environment-aware, reproducible",
        }

    @property
    def default(self) -> str:
        return "pkg"
