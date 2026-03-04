<!-- path: promptosaurus/prompts/core-conventions-swift.md -->
# Swift Conventions

Language:             {{LANGUAGE}}           e.g., Swift 5.9
Runtime:              {{RUNTIME}}            e.g., macOS, iOS, Linux
Package Manager:      {{SWIFT_PACKAGE_MANAGER}}               e.g., Swift Package Manager, CocoaPods
Linter:               {{LINTER}}             e.g., SwiftLint
Formatter:           {{FORMATTER}}          e.g., SwiftFormat

## Swift-Specific Rules

### Type System
- Use value types (structs, enums) by default
- Use classes only when needed (reference semantics, inheritance)
- Use optionals (? and !) appropriately
- Use protocols for abstraction

### Error Handling
- Use throws for error handling
- Use Result type where appropriate
- Never use force unwrap (!) unless certain

### Code Style
- Follow Swift API Design Guidelines
- Use SwiftLint for linting
- Use SwiftFormat for formatting

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%

#### Test Types

##### Unit Tests
- Use XCTest for testing
- Test one type/method in isolation
- Use mocks for dependencies

##### UI Tests
- Use XCUITest for UI testing

##### Snapshot Tests
- Use SwiftSnapshotTesting for visual testing

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., XCTest
Mocking:        {{MOCKING_LIBRARY}}              e.g., Mockingbird
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Xcode coverage

#### Scaffolding

```bash
# Install
swift test                    # Run tests
swift test --enable-code-coverage  # With coverage

# Configuration (Package.swift)
.target(
    name: "MyApp",
    dependencies: [],
    path: "Sources"
)

# SwiftLint
swiftlint --config .swiftlint.yml

# SwiftFormat
swiftformat .
```
