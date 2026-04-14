# Haskell build tool question

from promptosaurus.questions.base.question import Question


class HaskellBuildToolQuestion(Question):
    """Question handler for Haskell build tool."""

    @property
    def key(self) -> str:
        return "haskell_build_tool"

    @property
    def question_text(self) -> str:
        return "What build tool do you want to use for Haskell?"

    @property
    def explanation(self) -> str:
        return """Build tools manage dependencies, compilation, and project structure.

- Stack provides reproducible builds and isolated environments
- Cabal is the traditional build tool with direct package management
- Stack is generally recommended for new projects"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["Cabal", "Stack", "Nix"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "Cabal"

    config_key = "build_tool"
