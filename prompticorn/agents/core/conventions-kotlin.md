<!-- path: prompticorn/prompts/agents/core/core-conventions-kotlin.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
# Core Conventions Kotlin

Language:             {{ language or "e.g., Kotlin 1.9" }}
Runtime:              {{ runtime or "e.g., JVM 21, Kotlin/JS, Kotlin/Native" }}
Build tool:           {{ build_tool or "e.g., Gradle, Maven" }}
Linter:               {{ linter or "e.g., ktlint, detekt" }}
Formatter:           {{ formatter or "e.g., ktlint" }}

### Naming Conventions

Files:               PascalCase
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Kotlin-Specific Rules

### Null Safety
- Use nullable types (?) for values that can be null
- Use safe call operator (?.) and elvis operator (?:)
- Prefer val over var
- Avoid null checks, use built-in operators

### Error Handling
- Use Result for fallible operations
- Use exceptions for truly exceptional cases
- Use sealed classes for error types

### Coroutines
- Use suspend functions for async operations
- Use structured concurrency
- Use Flow for streams of data

{{ testing.render_testing_section(language, test_framework, coverage_targets) }}
