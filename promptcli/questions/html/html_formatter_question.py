# HTML formatter question

from promptcli.questions.base.question import Question


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
        return ["prettier", "html-beautify (js-beautify)", "djLint", "none"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "prettier": "Most popular - handles HTML, CSS, JS in one tool",
            "html-beautify (js-beautify)": "Lightweight HTML-focused formatter",
            "djLint": "Best for template files (Django, Jinja2, Handlebars)",
            "none": "No formatter - manual formatting only",
        }

    @property
    def default(self) -> str:
        return "prettier"
