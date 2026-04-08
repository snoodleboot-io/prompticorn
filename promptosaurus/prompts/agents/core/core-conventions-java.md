<!-- path: promptosaurus/prompts/agents/core/core-conventions-java.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions Java

Language:             {{config.language}}           e.g., Java 21
Runtime:              {{config.runtime}}            e.g., JDK 21, OpenJDK
Package Manager:      {{config.package_manager}}        e.g., Maven, Gradle
Linter:               {{config.linter}}             e.g., Checkstyle, SpotBugs
Formatter:           {{config.formatter}}          e.g., Google Java Format, Spotless

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

### Testing

{{ testing.render_test_types('java') }}

{{ coverage.render_coverage_table(
  line=config.coverage.line | default('80'),
  branch=config.coverage.branch | default('70'),
  function=config.coverage.function | default('90'),
  statement=config.coverage.statement | default('85'),
  mutation=config.coverage.mutation | default('80'),
  path=config.coverage.path | default('60')
) }}
