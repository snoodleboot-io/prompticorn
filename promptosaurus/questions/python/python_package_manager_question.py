"""Question for selecting Python package manager."""

from promptosaurus.questions.base.question import Question


class PythonPackageManagerQuestion(Question):
    """Question handler for Python package manager selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_package_manager"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What package manager?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return (
            "Choose your preferred Python package manager for dependency and virtual environment management.\n"
            "Different managers offer different approaches: pip is the standard library tool,\n"
            "poetry and pipenv provide advanced features like Dependency resolution and lock files,\n"
            "uv is a modern fast alternative, and conda handles cross-platform packages and environments."
        )

    @property
    def options(self) -> list[str]:
        """Available package managers."""
        return ["uv", "pip", "poetry", "pipenv", "conda"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "uv"

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "uv": "Ultra-fast modern replacement for pip, instant installations (recommended)",
            "pip": "Simplest, built-in package manager for Python",
            "uv": "Ultra-fast modern replacement for pip, instant installations (recommended)",
            "poetry": "Dependency management with lock files, publish to PyPI",
            "pipenv": "Combines pip and virtualenv, integrates environment management",
            "conda": "Cross-platform, handles non-Python dependencies",
        }
