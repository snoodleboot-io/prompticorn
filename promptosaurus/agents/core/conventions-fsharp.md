<!-- path: promptosaurus/prompts/agents/core/core-conventions-fsharp.md -->
# Core Conventions F

Language:             {{ language }} e.g., F# 7.0
Runtime:              {{ runtime }} e.g., .NET 8
Package Manager:      {{ package_manager }} e.g., NuGet, dotnet
Linter:               {{ linter }} e.g., Fantomas
Formatter:           {{ formatter }} e.g., Fantomas

### Naming Conventions

Files:              PascalCase
Variables:          camelCase
Constants:          PascalCase
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## F#-Specific Rules

### Type System
- Use discriminated unions
- Use record types for data
- Use Option for optional values

### Error Handling
- Use Result for error handling
- Use Option for optional values

### Code Style
- Follow F# style guide
- Use pipe operator

### Testing
Framework:       [Template variable]        e.g., NUnit, xUnit, Expecto
Coverage tool:  [Template variable]              e.g., Coverlet
