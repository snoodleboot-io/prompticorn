<!-- path: prompticorn/prompts/agents/core/core-conventions-groovy.md -->
# Core Conventions Groovy

Language:             {{ language or "e.g., Groovy 4.0" }}
Runtime:              {{ runtime or "e.g., JVM" }}
Package Manager:      {{ package_manager or "e.g., Gradle" }}
Linter:               {{ linter or "e.g., CodeNarc" }}
Formatter:           {{ formatter or "e.g., groovyfmt" }}

### Naming Conventions

Files:              snake_case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Groovy-Specific Rules

### Type System
- Use static typing with @TypeChecked when needed
- Use dynamic typing for scripting

### Error Handling
- Use exceptions for error handling

### Code Style
- Follow Groovy style guide

### Testing
Framework:       {{ test_framework or "e.g., Spock" }}
Coverage tool:  {{ coverage_tool or "e.g., JaCoCo" }}
