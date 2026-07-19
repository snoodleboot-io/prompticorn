<!-- path: prompticorn/prompts/agents/core/core-conventions-java.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
# Core Conventions Java

Language:             {{ language or "e.g., Java 21" }}
Runtime:              {{ runtime or "e.g., JDK 21, OpenJDK" }}
Build tool:           {{ build_tool or "e.g., Maven, Gradle" }}
Linter:               {{ linter or "e.g., Checkstyle, SpotBugs" }}
Formatter:           {{ formatter or "e.g., Google Java Format, Spotless" }}

### Naming Conventions

Files:               PascalCase
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Java-Specific Rules

### Type System
- Use strong typing - avoid raw types
- Prefer immutable objects where possible
- Use Optional for nullable return types
- Enable checker framework for null annotations

### Error Handling
- Use specific exception types, not generic Exception
- Never catch Exception or Throwable unless rethrowing
- Use try-with-resources for all Closeable resources
- Log at the boundary where the error is handled

### Imports & Packages
- Use standard package structure (com.company.module)
- Group imports: java → javax → third-party → internal
- Never use wildcard imports (*)

{{ testing.render_testing_section(language, test_framework, coverage_targets) }}
