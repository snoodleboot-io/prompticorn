# HTML formatter question

from prompticorn.questions.base.question import Question


class HtmlFormatterQuestion(Question):
    """Question handler for HTML formatter/linter choice."""

    @property
    def key(self) -> str:
        return "html_formatter"

    @property
    def question_text(self) -> str:
        return "Which HTML formatter do you want to use?"

    @property
    def explanation(self) -> str:
        return """HTML formatters ensure consistent code style and catch common errors.

- Prettier is the most popular, handles HTML + embedded CSS/JS
- html-beautify is lightweight and HTML-focused
- djLint adds template language support (Django, Jinja2, etc.)"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["Prettier", "html-beautify", "djLint"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "Prettier"

    config_key = "formatter"
