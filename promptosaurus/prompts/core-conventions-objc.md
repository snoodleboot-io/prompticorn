<!-- path: promptosaurus/prompts/core-conventions-objc.md -->
# Objective-C Conventions

Language:             {{LANGUAGE}}           e.g., Objective-C
Runtime:              {{RUNTIME}}            e.g., macOS, iOS
Package Manager:      {{PACKAGE_MANAGER}}        e.g., CocoaPods, Carthage
Linter:              {{LINTER}}             e.g., clang-tidy
Formatter:           {{FORMATTER}}          e.g., clang-format

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%

#### Test Types
- Use XCTest for testing
- Use OCMock for mocking

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., XCTest
Mocking:        {{MOCKING_LIBRARY}}              e.g., OCMock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Xcode coverage
