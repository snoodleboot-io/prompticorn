# Clojure build tool question

from promptosaurus.questions.base.question import Question


class ClojureBuildToolQuestion(Question):
    """Question handler for Clojure build tool."""

    @property
    def key(self) -> str:
        return "clojure_build_tool"

    @property
    def question_text(self) -> str:
        return "What build tool do you want to use for Clojure?"

    @property
    def explanation(self) -> str:
        return """Build tools manage dependencies and project lifecycle.

- deps.edn is the modern, official tooling with CLI tools
- Leiningen is the traditional build tool with extensive plugin ecosystem
- Boot is a programmable build tool for complex workflows"""
