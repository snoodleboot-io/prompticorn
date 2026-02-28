# Haskell compiler question

from promptcli.questions.base.question import Question


class HaskellCompilerQuestion(Question):
    """Question handler for Haskell compiler."""

    @property
    def key(self) -> str:
        return "haskell_compiler"

    @property
    def question_text(self) -> str:
        return "What Haskell compiler do you want to use?"

    @property
    def explanation(self) -> str:
        return """The Haskell compiler translates Haskell code into executable programs.

- GHC (Glasgow Haskell Compiler) is the standard and most widely used compiler
- It provides advanced optimizations and language extensions
- GHC is the de facto standard for Haskell development"""

    @property
    def options(self) -> list[str]:
        return ["ghc"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "ghc": "Glasgow Haskell Compiler - the standard Haskell compiler",
        }

    @property
    def default(self) -> str:
        return "ghc"
