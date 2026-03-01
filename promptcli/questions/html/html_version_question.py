# HTML version question

from promptcli.questions.base.question import Question


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
        return ["HTML5", "HTML4 Strict", "XHTML5"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "HTML5": "Modern standard - semantic elements, native APIs, all browsers",
            "HTML4 Strict": "Legacy - maximum compatibility with older systems",
            "XHTML5": "XML-compliant HTML5 - strict parsing, required for some tools",
        }

    @property
    def default(self) -> str:
        return "HTML5"
