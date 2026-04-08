<!-- path: promptosaurus/prompts/agents/core/core-conventions-objc.md -->
# Core Conventions Objective-C

Language:             {{config.language}}           e.g., Objective-C
Runtime:              {{config.runtime}}            e.g., macOS, iOS
Package Manager:      {{config.package_manager}}        e.g., CocoaPods, Carthage
Linter:              {{config.linter}}             e.g., clang-tidy
Formatter:           {{config.formatter}}          e.g., clang-format

### Naming Conventions

Files:              PascalCase or snake_case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Objective-C-Specific Rules

### Memory Management
- Use ARC (Automatic Reference Counting)
- Avoid manual retain/release
- Use weak references for delegates

### Error Handling
- Use NSError for error handling
- Check return values for errors
- Use exceptions sparingly

### Code Style
- Follow Apple's coding guidelines
- Use camelCase for methods
- Use PascalCase for class names

### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%

#### Test Types
- Use XCTest for testing
- Use OCMock for mocking

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., XCTest
Mocking:        {{config.mocking_library}}              e.g., OCMock
Coverage tool:  {{config.coverage_tool}}              e.g., Xcode coverage
