# PHP package manager question

from promptosaurus.questions.base.question import Question


class PhpPackageManagerQuestion(Question):
    """Question handler for PHP package manager."""

    @property
    def key(self) -> str:
        return "php_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for PHP?"

    @property
    def explanation(self) -> str:
        return """Package managers handle dependency installation and autoloading.

- Composer is the de facto standard for PHP dependency management
- It handles PSR-4 autoloading, version constraints, and package discovery"""
