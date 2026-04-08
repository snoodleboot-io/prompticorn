<!-- path: promptosaurus/prompts/agents/core/core-conventions-elm.md -->
# Core Conventions Elm

Language:             {{config.language}}           e.g., Elm 0.19
Runtime:              {{config.runtime}}            e.g., Browser, Node.js
Package Manager:      {{config.package_manager}}        e.g., elm
Linter:               {{config.linter}}             e.g., elm-format, elm-review
Formatter:           {{config.formatter}}          e.g., elm-format

### Naming Conventions

Files:              PascalCase
Variables:          camelCase
Constants:          PascalCase
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Elm-Specific Rules

### Architecture
- Use The Elm Architecture (Model, View, Update)
- Keep Msg types small and focused
- Use Html.App for main application
- Separate commands from model updates

### Type System
- Use type annotations on exposed functions
- Prefer custom types over booleans
- Use Maybe and Result for absence/errors
- Leverage type inference

### Error Handling
- Use Result for fallible operations
- Use Maybe for optional values
- No runtime exceptions by design

### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Path:           {{config.coverage.path}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use elm-test for testing
- Test decoder functions
- Test update functions
- Test pure functions

##### Property Tests
- Use fuzz testing with elm-test

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., elm-test
Fuzz tool:      {{config.fuzz_tool}}            e.g., elm-test (built-in)
Coverage tool:  {{config.coverage_tool}}              e.g., elm-coverage

#### Scaffolding

```bash
# Install
elm install elm/json
elm install elm-explorations/test

# Run tests
elm-test                      # Run tests
elm-test --seed 1234         # With specific seed
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: elm-test
```
