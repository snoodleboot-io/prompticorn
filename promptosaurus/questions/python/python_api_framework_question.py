"""Python API framework question for backend/api folders."""

from promptosaurus.questions.base.question import Question


class PythonAPIFrameworkQuestion(Question):
    """Question for Python API framework (FastAPI, Flask, Django).

    This is a FUNGIBLE question - asked for each backend/api folder.
    Different API folders can use different frameworks.
    """

    @property
    def key(self) -> str:
        return "framework"

    @property
    def prompt(self) -> str:
        return "Python API framework"

    @property
    def default(self) -> str:
        return "fastapi"

    @property
    def explanation(self) -> str:
        return "Python API framework affects how you build web APIs, including routing, validation, and async support."

    @property
    def question_text(self) -> str:
        """Get the question text."""
        return "What API framework does this project use?"

    @property
    def options(self) -> list[str]:
        """Get API framework options."""
        return [
            "fastapi",
            "flask",
            "django",
            "starlette",
            "none",
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Get explanations for each option."""
        return {
            "fastapi": "Modern async framework with automatic OpenAPI docs, type validation, excellent performance",
            "flask": "Lightweight and flexible, minimal dependencies, easy to learn and extend",
            "django": "Full-featured framework with ORM, admin interface, built-in authentication and permissions",
            "starlette": "Minimal ASGI framework for advanced use cases, excellent for microservices",
            "none": "No framework - using only Python standard library",
        }

    def format_prompt(self) -> list:
        """Format the question prompt for display."""
        return [self.question_text]
