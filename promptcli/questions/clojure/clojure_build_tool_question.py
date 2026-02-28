# Clojure build tool question

from promptcli.questions.base.question import Question


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

    @property
    def options(self) -> list[str]:
        return ["deps.edn", "leiningen", "boot"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "deps.edn": "Modern official tooling - simple, fast, recommended for new projects",
            "leiningen": "Traditional tool - extensive plugin ecosystem, widely used",
            "boot": "Programmable builds - for complex custom workflows",
        }

    @property
    def default(self) -> str:
        return "deps.edn"
