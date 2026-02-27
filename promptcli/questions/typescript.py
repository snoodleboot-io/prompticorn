# TypeScript language questions

from promptcli.questions.base import Question


class TypeScriptVersionQuestion(Question):
    """Question handler for TypeScript version."""

    @property
    def key(self) -> str:
        return "typescript_version"

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


class TypeScriptPackageManagerQuestion(Question):
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


class TypeScriptTestFrameworkQuestion(Question):
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


class TypeScriptFrameworkQuestion(Question):
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
