<!-- path: promptosaurus/prompts/agents/core/core-conventions-swift.md -->
# Core Conventions Swift

Language:             {{ language }} e.g., Swift 5.9
Runtime:              {{ runtime }} e.g., macOS, iOS, Linux
Package Manager:      {{ package_manager }} e.g., Swift Package Manager, CocoaPods
Linter:               {{ linter }} e.g., SwiftLint
Formatter:           {{ formatter }} e.g., SwiftFormat

### Naming Conventions

Files:               PascalCase
Variables:          camelCase
Constants:          camelCase or UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

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
Line:           [Template variable]          e.g., 80%
Branch:         [Template variable]        e.g., 70%
Function:       [Template variable]       e.g., 90%
Statement:      [Template variable]      e.g., 85%

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
Framework:       [Template variable]        e.g., XCTest
Mocking:        [Template variable]              e.g., Mockingbird
Coverage tool:  [Template variable]              e.g., Xcode coverage

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
