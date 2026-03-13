"""Python UI framework question for frontend/ui folders."""

from promptosaurus.questions.base.question import Question


class PythonUIFrameworkQuestion(Question):
    """Question for Python UI framework (Dash, Streamlit, Reflex).

    This is a FUNGIBLE question - asked for each frontend/ui folder.
    Different UI folders can use different frameworks.
    """

    @property
    def key(self) -> str:
        return "framework"

    @property
    def prompt(self) -> str:
        return "Python UI framework"

    @property
    def default(self) -> str:
        return "streamlit"

    @property
    def explanation(self) -> str:
        return "Python UI framework affects how you build user interfaces, including data visualization and interactivity."

    @property
    def question_text(self) -> str:
        """Get the question text."""
        return "What UI framework does this project use?"

    @property
    def options(self) -> list[str]:
        """Get UI framework options."""
        return [
            "streamlit",
            "dash",
            "reflex",
            "nicegui",
            "shiny",
            "none",
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Get explanations for each option."""
        return {
            "streamlit": "Streamlit - rapid prototyping, data apps",
            "dash": "Dash - Plotly-based, analytical apps",
            "reflex": "Reflex (Pynecone) - full-stack Python web apps",
            "nicegui": "NiceGUI - simple GUI library",
            "shiny": "Shiny for Python - R Shiny port",
            "none": "No framework - using templates only",
        }

    def format_prompt(self) -> list:
        """Format the question prompt for display."""
        return [self.question_text]
