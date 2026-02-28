# TypeScript framework question

from promptcli.questions.base.question import Question


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
