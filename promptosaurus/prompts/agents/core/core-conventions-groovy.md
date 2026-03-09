<!-- path: promptosaurus/prompts/agents/core/core-conventions-groovy.md -->
# Core Conventions Groovy

Language:             {{LANGUAGE}}           e 4.0.g., Groovy
Runtime:              {{RUNTIME}}            e.g., JVM
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Gradle
Linter:              {{LINTER}}             e.g., CodeNarc
Formatter:           {{FORMATTER}}          e.g., groovyfmt

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., Spock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., JaCoCo
