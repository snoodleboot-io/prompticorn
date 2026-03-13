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
            "none": "No framework - using stdlib only",
            "fastapi": "FastAPI - modern, async, auto-docs",
            "flask": "Flask - lightweight, flexible",
            "django": "Django - full-featured, ORM",
            "starlette": "Starlette - ASGI minimal",
            "streamlit": "Streamlit - data apps",
            "dash": "Dash - Plotly analytical",
            "celery": "Celery - task queue",
            "huey": "Huey - lightweight task queue",
            "dramatiq": "Dramatiq - modern task queue",
        }

    def format_prompt(self) -> list:
        """Format the question prompt for display."""
        return [self.question_text]
