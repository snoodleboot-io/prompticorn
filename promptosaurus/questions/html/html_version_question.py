# HTML version question

from promptosaurus.questions.base.question import Question


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
