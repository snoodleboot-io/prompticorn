# Shell type question

from promptosaurus.questions.base.question import Question


class ShellTypeQuestion(Question):
    """Question handler for shell type."""

    @property
    def key(self) -> str:
        return "shell_type"

    @property
    def question_text(self) -> str:
        return "What shell do you want to target?"

    @property
    def explanation(self) -> str:
        return """Different shells have different syntax and features.

- Bash is the most widely available and standard shell
- Zsh has modern features and is the default on macOS
- Fish has user-friendly syntax but is less POSIX-compatible"""

    @property
    def options(self) -> list[str]:
        return ["bash", "zsh", "fish"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "bash": "Bourne Again Shell - most portable, widely available, recommended",
            "zsh": "Z Shell - modern features, macOS default",
            "fish": "Friendly Interactive Shell - user-friendly, not POSIX-compatible",
        }

    @property
    def default(self) -> str:
        return "bash"
