# HTML version question

from prompticorn.questions.base.question import Question


class HtmlVersionQuestion(Question):
    """Question handler for HTML version/specification."""

    @property
    def key(self) -> str:
        return "html_version"

    @property
    def question_text(self) -> str:
        return "Which HTML specification do you want to target?"

    @property
    def explanation(self) -> str:
        return """HTML version determines feature availability and browser compatibility.

- HTML5 is the current standard with broad browser support
- HTML4/XHTML are legacy formats for specific compatibility needs
- Strict/Transitional affects validation rules"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["HTML5", "XHTML 1.0 Strict", "XHTML 1.0 Transitional", "HTML 4.01"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "HTML5"

    config_key = "html_version"
