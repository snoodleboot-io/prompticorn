<!-- path: promptosaurus/prompts/core-conventions-cs.md -->
# C# Conventions

Language:             {{LANGUAGE}}           e.g., C# 12, .NET 8
Runtime:              {{RUNTIME}}            e.g., .NET 8, Mono
Package Manager:      {{PACKAGE_MANAGER}}        e.g., NuGet, dotnet
Linter:               {{LINTER}}             e.g., StyleCop, SonarLint
Formatter:           {{FORMATTER}}          e.g., dotnet format, ReSharper

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Mutation:       {{MUTATION_COVERAGE_%}}       e.g., 80%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., xUnit, NUnit, MSTest
Mocking library: {{MOCKING_LIBRARY}}              e.g., Moq, NSubstitute
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Coverlet, dotnet-coverage

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
