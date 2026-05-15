<!-- path: prompticorn/prompts/agents/core/core-conventions-groovy.md -->
# Core Conventions Groovy

Language:             {{ language }} e 4.0.g., Groovy
Runtime:              {{ runtime }} e.g., JVM
Package Manager:      {{ package_manager }} e.g., Gradle
Linter:               {{ linter }} e.g., CodeNarc
Formatter:           {{ formatter }} e.g., groovyfmt

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
Framework:       [Template variable]        e.g., Spock
Coverage tool:  [Template variable]              e.g., JaCoCo
