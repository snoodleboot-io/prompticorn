# Language-specific question classes using sweet_tea

from sweet_tea import AbstractFactory
from sweet_tea.entry import entry

from promptcli.questions.base import BaseQuestion

# ══════════════════════════════════════════════════════════════════════════════
# Python Questions
# ══════════════════════════════════════════════════════════════════════════════


@entry(library="promptcli", label="language")
class PythonQuestion(BaseQuestion):
    """Question handler for Python projects."""

    @property
    def key(self) -> str:
        return "python"

    @property
    def question_text(self) -> str:
        return "What Python runtime version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Python runtime affects package compatibility, performance, and available features.

- Newer versions have better performance but may have compatibility issues
- Some packages only support specific versions
- match statements require 3.10+, walrus operator requires 3.8+"""

    @property
    def options(self) -> list[str]:
        return ["3.12", "3.11", "3.10", "3.9", "PyPy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "3.12": "Latest stable - best performance, recommended for new projects",
            "3.11": "Very stable - excellent performance improvements over 3.10",
            "3.10": "Stable - pattern matching (match/case), better error messages",
            "3.9": "Long-term support - maximum package compatibility",
            "PyPy": "JIT compiler - faster for long-running processes, good for servers",
        }

    @property
    def default(self) -> str:
        return "3.12"


@entry(library="promptcli", label="language")
class PythonPackageManagerQuestion(BaseQuestion):
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
        return ["poetry", "pip", "uv", "conda", "PDM"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "poetry": "Modern, all-in-one - dependency + env + build (recommended for new projects)",
            "pip": "Standard - simple, widely compatible, no lock file by default",
            "uv": "Extremely fast - Rust-based, good for CI/CD and large projects",
            "conda": "Data science focus - manages non-Python dependencies too",
            "PDM": "Modern PEP 582 - no virtualenv, good pyproject.toml integration",
        }

    @property
    def default(self) -> str:
        return "poetry"


@entry(library="promptcli", label="language")
class PythonTestFrameworkQuestion(BaseQuestion):
    """Question for Python test framework."""

    @property
    def key(self) -> str:
        return "python_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Testing framework affects:
- Test discovery and organization
- Assertion style and reporting
- Fixture and mocking capabilities
- Integration with coverage tools"""

    @property
    def options(self) -> list[str]:
        return ["pytest", "unittest", "doctest", "nose2"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "pytest": "Industry standard - powerful fixtures, great reporting, widely used",
            "unittest": "Built-in - simple, no dependencies, good for beginners",
            "doctest": "Documentation testing - tests in docstrings, good for math/code clarity",
            "nose2": "nose successor - plugin ecosystem, pytest-like",
        }

    @property
    def default(self) -> str:
        return "pytest"


@entry(library="promptcli", label="language")
class PythonLinterQuestion(BaseQuestion):
    """Question for Python linter."""

    @property
    def key(self) -> str:
        return "python_linter"

    @property
    def question_text(self) -> str:
        return "What linter do you want to use?"

    @property
    def explanation(self) -> str:
        return """Linter affects:
- Code quality checking
- Style enforcement
- Bug detection
- Type checking (for some)"""

    @property
    def options(self) -> list[str]:
        return ["ruff", "flake8", "pylint", "mypy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "ruff": "Ultra-fast (Rust) - modern, replaces flake8+isort, recommended",
            "flake8": "Classic - simple, stable, good default rules",
            "pylint": "Comprehensive - deep analysis, strict, many rules",
            "mypy": "Type checker - optional static typing enforcement",
        }

    @property
    def default(self) -> str:
        return "ruff"


@entry(library="promptcli", label="language")
class PythonFormatterQuestion(BaseQuestion):
    """Question for Python formatter."""

    @property
    def key(self) -> str:
        return "python_formatter"

    @property
    def question_text(self) -> str:
        return "What code formatter do you want to use?"

    @property
    def explanation(self) -> str:
        return """Formatter affects:
- Code style consistency
- Time saved on formatting debates
- Integration with pre-commit hooks"""

    @property
    def options(self) -> list[str]:
        return ["ruff", "black", "yapf"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "ruff": "Fastest (Rust) - format + lint in one, recommended",
            "black": "Most popular - opinionated, consistent, widely adopted",
            "yapf": "Google style - configurable, good for existing codebases",
        }

    @property
    def default(self) -> str:
        return "ruff"


# ══════════════════════════════════════════════════════════════════════════════
# TypeScript Questions
# ══════════════════════════════════════════════════════════════════════════════


@entry(library="promptcli", label="language")
class TypeScriptQuestion(BaseQuestion):
    """Question handler for TypeScript projects."""

    @property
    def key(self) -> str:
        return "typescript"

    @property
    def question_text(self) -> str:
        return "What TypeScript version do you want to use?"

    @property
    def explanation(self) -> str:
        return """TypeScript version affects available features and type system capabilities.

- Newer versions have better inference and more features
- Older versions have better ecosystem compatibility"""

    @property
    def options(self) -> list[str]:
        return ["5.4", "5.3", "5.2", "5.1", "5.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "5.4": "Latest stable - best inference, const type params, recommended",
            "5.3": "Recent stable - excellent all-around",
            "5.2": "Stable - decorators,/modifiers, narrowing",
            "5.1": "Long-term support - very stable, maximum compatibility",
            "5.0": "Major release - significant changes, may need updates",
        }

    @property
    def default(self) -> str:
        return "5.4"


@entry(library="promptcli", label="language")
class TypeScriptPackageManagerQuestion(BaseQuestion):
    """Question for TypeScript package manager."""

    @property
    def key(self) -> str:
        return "typescript_package_manager"

    @property
    def question_text(self) -> str:
        return "What package manager do you want to use for JavaScript/TypeScript?"

    @property
    def explanation(self) -> str:
        return """Package manager affects:
- Installation speed
- Lock file handling
- Workspace support
- Node version management"""

    @property
    def options(self) -> list[str]:
        return ["npm", "pnpm", "yarn"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "npm": "Official - largest ecosystem, good for most projects",
            "pnpm": "Fast, efficient - disk space savings, strict node_modules",
            "yarn": "Facebook - good features, widely used, npm alternative",
        }

    @property
    def default(self) -> str:
        return "npm"


@entry(library="promptcli", label="language")
class TypeScriptTestFrameworkQuestion(BaseQuestion):
    """Question for TypeScript test framework."""

    @property
    def key(self) -> str:
        return "typescript_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Testing framework affects:
- Unit and integration testing
- Mocking capabilities
- Assertion syntax
- Coverage reporting"""

    @property
    def options(self) -> list[str]:
        return ["vitest", "jest", "mocha"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "vitest": "Fast, modern - Vite-native, great DX, recommended for new projects",
            "jest": "Popular - Facebook-maintained, great ecosystem, widely used",
            "mocha": "Flexible - simple, good for legacy projects",
        }

    @property
    def default(self) -> str:
        return "vitest"


@entry(library="promptcli", label="language")
class TypeScriptFrameworkQuestion(BaseQuestion):
    """Question for TypeScript framework (React, Vue, etc)."""

    @property
    def key(self) -> str:
        return "typescript_framework"

    @property
    def question_text(self) -> str:
        return "What frontend framework are you using?"

    @property
    def explanation(self) -> str:
        return """Frontend framework affects:
- Component structure
- State management patterns
- Build configuration
- Type definitions needed"""

    @property
    def options(self) -> list[str]:
        return ["none", "react", "vue", "svelte", "angular", "nextjs", "nuxt"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "none": "Vanilla TypeScript - no framework, just JS/TS",
            "react": "Meta - most popular, huge ecosystem, flexible",
            "vue": "Evan You - approachable, progressive, great docs",
            "svelte": "Rich Harris - compile-time, less boilerplate",
            "angular": "Google - enterprise, TypeScript-first, full framework",
            "nextjs": "Vercel - React meta-framework, SSR/SSG",
            "nuxt": "Vue meta-framework - SSR/SSG for Vue",
        }

    @property
    def default(self) -> str:
        return "none"


# ══════════════════════════════════════════════════════════════════════════════
# Question Factory using sweet_tea AbstractFactory
# ══════════════════════════════════════════════════════════════════════════════


# Create the question factory using sweet_tea's AbstractFactory
QuestionFactory = AbstractFactory[BaseQuestion]

# Registry of available language keys for dynamic lookup
LANGUAGE_KEYS = [
    "python",
    "typescript",
    "javascript",
    "java",
    "csharp",
    "go",
    "rust",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "elixir",
    "elm",
    "haskell",
    "clojure",
    "fsharp",
    "dart",
    "julia",
    "lua",
    "r",
    "shell",
    "groovy",
    "terraform",
    "sql",
]


def get_language_questions(language: str) -> list[BaseQuestion]:
    """
    Get all questions for a specific language.

    Returns a list of questions that should be asked for the given language.
    """
    questions: list[BaseQuestion] = []
    lang = language.lower()

    if lang == "python":
        questions.extend(
            [
                PythonQuestion(),
                PythonPackageManagerQuestion(),
                PythonTestFrameworkQuestion(),
                PythonLinterQuestion(),
                PythonFormatterQuestion(),
            ]
        )
    elif lang == "typescript" or lang == "javascript":
        questions.extend(
            [
                TypeScriptQuestion(),
                TypeScriptPackageManagerQuestion(),
                TypeScriptTestFrameworkQuestion(),
                TypeScriptFrameworkQuestion(),
            ]
        )

    return questions
