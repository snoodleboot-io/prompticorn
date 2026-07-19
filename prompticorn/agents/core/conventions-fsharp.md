<!-- path: prompticorn/prompts/agents/core/core-conventions-fsharp.md -->
# Core Conventions F

Language:             {{ language or "e.g., F# 7.0" }}
Runtime:              {{ runtime or "e.g., .NET 8" }}
Package Manager:      {{ package_manager or "e.g., NuGet, dotnet" }}
Linter:               {{ linter or "e.g., Fantomas" }}
Formatter:           {{ formatter or "e.g., Fantomas" }}
{% if framework %}Framework:            {{ framework or "e.g., Giraffe, Saturn, Fable" }}
{% endif %}

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
Framework:       {{ test_framework or "e.g., NUnit, xUnit, Expecto" }}
Coverage tool:  {{ coverage_tool or "e.g., Coverlet" }}
