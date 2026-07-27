"""Question for selecting the JavaScript (ECMAScript) language version.

This module defines the JavaScriptVersionQuestion class which prompts users to
select the ECMAScript edition their project targets. JavaScript's version is the
yearly ECMAScript edition (ES2026, ES2025, ...), which is distinct from the
runtime that executes it (Node.js, Deno, Bun) — see the ``runtime`` field in the
convention for the engine.

Before PRO-94 the JavaScript pipeline reused ``TypeScriptVersionQuestion``, so a
JS project was asked for a TypeScript version. This offers the correct
ECMAScript editions instead.
"""

from prompticorn.questions.base.question import Question


class JavaScriptVersionQuestion(Question):
    """Question handler for JavaScript (ECMAScript) edition selection.

    The ECMAScript edition determines which language features are available.
    Editions are published yearly; ES2015 (ES6) is the modern baseline. The
    selection is stored as the language's ``runtime`` value, matching every other
    language's version question.

    Attributes:
        key: Unique identifier for this question
        question_text: The question presented to the user
        explanation: Detailed explanation of ECMAScript editions
        options: Available ECMAScript editions
        option_explanations: Why each edition exists
        default: Default edition selection
        config_key: Configuration key where answer is stored
    """

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "javascript_version"

    @property
    def question_text(self) -> str:
        """The question text to display."""
        return "What JavaScript (ECMAScript) edition?"

    @property
    def explanation(self) -> str:
        """Explanation of why this question matters."""
        return """Select the ECMAScript edition your project targets.

The edition determines available language features and syntax. It is separate
from the runtime that executes the code (Node.js, Deno, Bun)."""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["ES2026", "ES2025", "ES2024", "ES2023", "ES2022", "ES2021", "ES2020", "ES2015"]

    @property
    def option_explanations(self) -> dict[str, str]:
        """Why each edition exists."""
        return {
            "ES2026": "ECMAScript 2026 - Latest edition (Temporal, explicit resource management)",
            "ES2025": "ECMAScript 2025 - Iterator helpers, Set methods, JSON modules",
            "ES2024": "ECMAScript 2024 - Well-supported recent edition",
            "ES2023": "ECMAScript 2023 - Array find-from-last, hashbang grammar",
            "ES2022": "ECMAScript 2022 - Top-level await, class fields",
            "ES2021": "ECMAScript 2021 - Logical assignment, numeric separators",
            "ES2020": "ECMAScript 2020 - Optional chaining, nullish coalescing, BigInt",
            "ES2015": "ECMAScript 2015 (ES6) - The modern JavaScript baseline",
        }

    @property
    def default(self) -> str:
        """Default selection."""
        return "ES2026"

    config_key = "runtime"
