<!-- path: promptosaurus/prompts/agents/core/core-conventions-groovy.md -->
# Core Conventions Groovy

Language:             {{config.language}}           e 4.0.g., Groovy
Runtime:              {{config.runtime}}            e.g., JVM
Package Manager:      {{config.package_manager}}        e.g., Gradle
Linter:              {{config.linter}}             e.g., CodeNarc
Formatter:           {{config.formatter}}          e.g., groovyfmt

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
Framework:       {{config.testing_framework}}        e.g., Spock
Coverage tool:  {{config.coverage_tool}}              e.g., JaCoCo
