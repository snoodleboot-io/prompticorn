# Go version question

from promptosaurus.questions.base.question import Question


class GoVersionQuestion(Question):
    """Question handler for Go version selection."""

    @property
    def key(self) -> str:
        return "go_version"

    @property
    def question_text(self) -> str:
        return "What Go version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Go version affects module compatibility, performance, and language features.

- Newer versions have better performance and runtime improvements
- Go modules (go.mod) became the standard in 1.13+
- Generics support was added in Go 1.18
- Some libraries require minimum Go versions"""

    @property
    def options(self) -> list[str]:
        return ["1.22", "1.21", "1.20", "1.19"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "1.22": "Latest stable - improved HTTP routing, better loop variable semantics",
            "1.21": "Very stable - built-in min/max functions, improved slog package",
            "1.20": "Stable - context with cancel cause, unsafe.SliceData, strings.CutPrefix",
            "1.19": "Mature - generics available, minimal changes, maximum compatibility",
        }

    @property
    def default(self) -> str:
        return "1.22"
