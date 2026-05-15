# Python package manager question

from prompticorn.questions.base.question import Question


class PythonPackageManagerQuestion(Question):
    """Question for Python package manager."""

    @property
    def key(self) -> str:
        return "python_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for Python?"

    @property
    def explanation(self) -> str:
        return """Package manager affects:
- Dependency resolution and lock file management
- Virtual environment handling
- Build system integration
- Publishing to PyPI"""

    @property
    def options(self) -> list[str]:
        return ["uv", "pip", "poetry", "pipenv", "conda"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "uv": "Ultra-fast modern replacement for pip, instant installations (recommended)",
            "pip": "Simplest, built-in package manager for Python",
            "poetry": "Dependency management with lock files, publish to PyPI",
            "pipenv": "Combines pip and virtualenv, integrates environment management",
            "conda": "Cross-platform, handles non-Python dependencies",
        }

    @property
    def default(self) -> str:
        return "uv"
