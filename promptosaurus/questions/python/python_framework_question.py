"""Python framework question for fungible configuration."""

from promptosaurus.questions.base.question import Question


class PythonFrameworkQuestion(Question):
    """Question about Python web framework.

    This is a FUNGIBLE question - asked for each folder, can differ per workspace.
    For example: backend/api might use fastapi, backend/worker might use flask.
    """

    @property
    def key(self) -> str:
        return "framework"

    @property
    def prompt(self) -> str:
        return "Python framework"

    @property
    def default(self) -> str:
        return "none"

    @property
    def explanation(self) -> str:
        return "Python framework affects how you build your application, including web APIs, UIs, or background workers."

    @property
    def question_text(self) -> str:
        """Get the question text."""
        return "What framework does this Python project use?"

    @property
    def options(self) -> list[str]:
        """Get framework options."""
        return [
            "none",
            "fastapi",
            "flask",
            "django",
            "starlette",
            "streamlit",
            "dash",
            "celery",
            "huey",
            "dramatiq",
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Get explanations for each option."""
        return {
            "none": "No framework - using only Python standard library",
            "fastapi": "Modern async API framework with automatic OpenAPI documentation and type hints",
            "flask": "Lightweight and flexible web framework, minimal core with extension ecosystem",
            "django": "Full-featured web framework with ORM, admin panel, and authentication",
            "starlette": "Minimal ASGI framework, powers FastAPI, for advanced use cases",
            "streamlit": "Rapid prototyping for data apps, simple Python script to interactive web app",
            "dash": "Analytical web apps with Plotly, enterprise-ready dashboards",
            "celery": "Distributed task queue for background jobs and scheduled tasks",
            "huey": "Simple lightweight task queue, alternative to Celery",
            "dramatiq": "Modern task queue with focus on simplicity, distributed job processing",
        }

    def format_prompt(self) -> list:
        """Format the question prompt for display."""
        return [self.question_text]
