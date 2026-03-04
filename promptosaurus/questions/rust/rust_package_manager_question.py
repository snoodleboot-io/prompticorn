# Rust package manager question

from promptosaurus.questions.base.question import Question


class RustPackageManagerQuestion(Question):
    """Question for Rust package manager."""

    @property
    def key(self) -> str:
        return "rust_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for Rust?"

    @property
    def explanation(self) -> str:
        return """Package manager affects dependency resolution, build configuration, and workspace management.

- Cargo is the official and only widely-used package manager for Rust
- It handles dependency resolution, building, testing, and publishing to crates.io
- Cargo.toml defines project metadata and dependencies
- Cargo.lock ensures reproducible builds"""

    @property
    def options(self) -> list[str]:
        return ["cargo"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "cargo": "Official Rust package manager - handles dependencies, builds, tests, and publishing",
        }

    @property
    def default(self) -> str:
        return "cargo"
