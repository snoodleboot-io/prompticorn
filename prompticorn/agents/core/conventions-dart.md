<!-- path: prompticorn/prompts/agents/core/core-conventions-dart.md -->
# Core Conventions Dart

Language:             {{ language or "e.g., Dart 3.2" }}
Runtime:              {{ runtime or "e.g., Flutter, Dart VM" }}
Package Manager:      {{ package_manager or "e.g., pub" }}
Linter:               {{ linter or "e.g., dart analyze" }}
Formatter:           {{ formatter or "e.g., dart format" }}

### Naming Conventions

Files:              snake_case
Variables:          camelCase
Constants:          camelCase or UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Dart-Specific Rules

### Null Safety
- Use null safety by default
- Use late for lazy initialization
- Use ? for nullable types

### Error Handling
- Use exceptions for error handling
- Use try/catch for exception handling

### Code Style
- Follow Dart style guide
- Use flutter test for Flutter projects

### Testing

#### Coverage Targets
Line:           {{ coverage_targets.get('line', '') or "e.g., 80%" }}
Branch:         {{ coverage_targets.get('branch', '') or "e.g., 70%" }}
Function:       {{ coverage_targets.get('function', '') or "e.g., 90%" }}

#### Test Types
- Use flutter_test or test package
- Use mockito for mocking

#### Framework & Tools
Framework:       {{ test_framework or "e.g., flutter_test, test" }}
Mocking:        {{ mocking_library or "e.g., mockito" }}
Coverage tool:  {{ coverage_tool or "e.g., coverage" }}
