# Ruby package manager question

from promptosaurus.questions.base.question import Question


class RubyPackageManagerQuestion(Question):
    """Question handler for Ruby package manager."""

    @property
    def key(self) -> str:
        return "ruby_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for Ruby?"

    @property
    def explanation(self) -> str:
        return """Package managers handle dependency installation and versioning.

- Bundler is the standard for application dependency management
- RubyGems is the built-in package manager for installing gems"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["Bundler", "RubyGems"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "Bundler"

    config_key = "package_manager"
