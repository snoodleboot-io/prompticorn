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
        return ["bundler", "rubygems"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "bundler": "Standard for apps - manages gem dependencies via Gemfile, recommended",
            "rubygems": "Built-in - direct gem installation, less common for projects",
        }

    @property
    def default(self) -> str:
        return "bundler"
