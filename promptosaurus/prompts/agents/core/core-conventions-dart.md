<!-- path: promptosaurus/prompts/agents/core/core-conventions-dart.md -->
# Core Conventions Dart

Language:             {{config.language}}           e.g., Dart 3.2
Runtime:              {{config.runtime}}            e.g., Flutter, Dart VM
Package Manager:      {{config.package_manager}}        e.g., pub
Linter:               {{config.linter}}             e.g., dart analyze
Formatter:           {{config.formatter}}          e.g., dart format

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
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%

#### Test Types
- Use flutter_test or test package
- Use mockito for mocking

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., flutter_test, test
Mocking:        {{config.mocking_library}}              e.g., mockito
Coverage tool:  {{config.coverage_tool}}              e.g., coverage
