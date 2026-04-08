<!-- path: promptosaurus/prompts/agents/core/core-conventions-kotlin.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions Kotlin

Language:             {{config.language}}           e.g., Kotlin 1.9
Runtime:              {{config.runtime}}            e.g., JVM 21, Kotlin/JS, Kotlin/Native
Package Manager:      {{config.package_manager}}        e.g., Gradle, Maven
Linter:               {{config.linter}}             e.g., ktlint, detekt
Formatter:           {{config.formatter}}          e.g., ktlint

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

### Testing

{{ testing.render_test_types('kotlin') }}

{{ coverage.render_coverage_table(
  line=config.coverage.line | default('80'),
  branch=config.coverage.branch | default('70'),
  function=config.coverage.function | default('90'),
  statement=config.coverage.statement | default('85'),
  mutation=config.coverage.mutation | default('80'),
  path=config.coverage.path | default('60')
) }}
