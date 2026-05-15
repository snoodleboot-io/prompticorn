"""Python worker framework question for backend/worker folders."""

from prompticorn.questions.base.question import Question


class PythonWorkerFrameworkQuestion(Question):
    """Question for Python worker/task queue framework (Celery, Huey, etc).

    This is a FUNGIBLE question - asked for each backend/worker folder.
    Different worker folders can use different frameworks.
    """

    @property
    def key(self) -> str:
        return "framework"

    @property
    def prompt(self) -> str:
        return "Python worker framework"

    @property
    def default(self) -> str:
        return "celery"

    @property
    def explanation(self) -> str:
        return "Worker framework affects how you handle background tasks, job queues, and async processing."

    @property
    def question_text(self) -> str:
        """Get the question text."""
        return "What worker/task queue framework does this project use?"

    @property
    def options(self) -> list[str]:
        """Get worker framework options."""
        return [
            "celery",
            "huey",
            "dramatiq",
            "rq",
            "none",
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Get explanations for each option."""
        return {
            "celery": "Celery - mature, feature-rich, Redis/RabbitMQ",
            "huey": "Huey - lightweight, simple, Redis/SQLite",
            "dramatiq": "Dramatiq - simple, modern, Redis/RabbitMQ",
            "rq": "RQ (Redis Queue) - simple, Redis-based",
            "none": "No worker - using threading/asyncio only",
        }

    def format_prompt(self) -> list:
        """Format the question prompt for display."""
        return [self.question_text]
