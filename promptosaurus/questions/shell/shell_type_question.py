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
        """Available options."""
        return ["bash", "zsh", "sh (POSIX)", "fish"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "bash"

    config_key = "shell_type"
