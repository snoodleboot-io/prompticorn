# Python package manager question

from promptosaurus.questions.base.question import Question


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
        return ["uv", "poetry", "pip", "conda", "pdm"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "uv": "Extremely fast - Rust-based, recommended for new projects (replaces pip)",
            "poetry": "Modern, all-in-one - dependency + env + build, widely used",
            "pip": "Standard - simple, widely compatible, no lock file by default",
            "conda": "Data science focus - manages non-Python dependencies too",
            "pdm": "Modern PEP 582 - no virtualenv, good pyproject.toml integration",
        }

    @property
    def default(self) -> str:
        return "uv"
