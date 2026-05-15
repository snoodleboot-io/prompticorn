<!-- path: prompticorn/prompts/agents/core/core-conventions-csharp.md -->
# Core Conventions C#

Language:             {{ language }} e.g., C# 12, .NET 8
Runtime:              {{ runtime }} e.g., .NET 8, Mono
Package Manager:      {{ package_manager }} e.g., NuGet, dotnet
Linter:               {{ linter }} e.g., StyleCop, SonarLint
Formatter:           {{ formatter }} e.g., dotnet format, ReSharper

### Naming Conventions

Files:               PascalCase
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    PascalCase
Environment vars:   UPPER_SNAKE_CASE always

## C#-Specific Rules

### Type System
- Use strong typing - avoid dynamic
- Prefer records for immutable data
- Use nullable reference types (`#nullable enable`)
- Implement IEquatable, IComparable where appropriate

### Error Handling
- Use exceptions for exceptional conditions
- Never catch Exception without rethrowing
- Use try/catch/finally or using statements for resources
- Use Result pattern for fallible operations

### Naming & Style
- Follow .NET naming conventions (PascalCase, camelCase)
- Use expression-bodied members where appropriate
- Use pattern matching and switch expressions

### Testing

#### Coverage Targets
Line:           [Template variable]          e.g., 80%
Branch:         [Template variable]        e.g., 70%
Function:       [Template variable]       e.g., 90%
Statement:      [Template variable]      e.g., 85%
Mutation:       [Template variable]       e.g., 80%
Path:           [Template variable]           e.g., 60%

#### Test Types

##### Unit Tests
- Use xUnit, NUnit, or MSTest
- One class or method in isolation
- Mock dependencies with Moq or NSubstitute

##### Integration Tests
- Test at service or API boundary
- Use TestContainers for databases
- Use WebApplicationFactory for ASP.NET testing

##### E2E Tests
- Use Playwright or Selenium for browser testing

##### Performance Tests
- Use BenchmarkDotNet for micro-benchmarks

#### Framework & Tools
Framework:       [Template variable]        e.g., xUnit, NUnit, MSTest
Mocking library: [Template variable]              e.g., Moq, NSubstitute
Coverage tool:  [Template variable]              e.g., Coverlet, dotnet-coverage

#### Scaffolding

```bash
# Install
dotnet add package xunit
dotnet add package Moq
dotnet add package coverlet.collector

# Run tests
dotnet test                     # Run tests
dotnet test --collect:"XPlat Code Coverage"  # With coverage
dotnet test --logger "console;verbosity=detailed"

# Configuration (.csproj)
<PropertyGroup>
  <CollectCoverage>true</CollectCoverage>
  <CoverletOutputFormat>opencover</CoverletOutputFormat>
</PropertyGroup>
```
