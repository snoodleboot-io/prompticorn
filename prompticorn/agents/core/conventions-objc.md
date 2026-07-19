<!-- path: prompticorn/prompts/agents/core/core-conventions-objc.md -->
# Core Conventions Objective-C

Language:             {{ language or "e.g., Objective-C" }}
Runtime:              {{ runtime or "e.g., macOS, iOS" }}
Package Manager:      {{ package_manager or "e.g., CocoaPods, Carthage" }}
Linter:               {{ linter or "e.g., clang-tidy" }}
Formatter:           {{ formatter or "e.g., clang-format" }}

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
Line:           {{ coverage_targets.get('line', '') or "e.g., 80%" }}
Branch:         {{ coverage_targets.get('branch', '') or "e.g., 70%" }}
Function:       {{ coverage_targets.get('function', '') or "e.g., 90%" }}

#### Test Types
- Use XCTest for testing
- Use OCMock for mocking

#### Framework & Tools
Framework:       {{ test_framework or "e.g., XCTest" }}
Mocking:        {{ mocking_library or "e.g., OCMock" }}
Coverage tool:  {{ coverage_tool or "e.g., Xcode coverage" }}
