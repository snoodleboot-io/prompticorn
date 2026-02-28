# Dart Conventions

Language:             {{LANGUAGE}}           e.g., Dart 3.2
Runtime:              {{RUNTIME}}            e.g., Flutter, Dart VM
Package Manager:      {{PACKAGE_MANAGER}}        e.g., pub
Linter:               {{LINTER}}             e.g., dart analyze
Formatter:           {{FORMATTER}}          e.g., dart format

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%

#### Test Types
- Use flutter_test or test package
- Use mockito for mocking

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., flutter_test, test
Mocking:        {{MOCKING_LIBRARY}}              e.g., mockito
Coverage tool:  {{COVERAGE_TOOL}}              e.g., coverage
