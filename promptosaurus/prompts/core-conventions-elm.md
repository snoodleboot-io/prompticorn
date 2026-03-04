<!-- path: promptosaurus/prompts/core-conventions-elm.md -->
# Elm Conventions

Language:             {{LANGUAGE}}           e.g., Elm 0.19
Runtime:              {{RUNTIME}}            e.g., Browser, Node.js
Package Manager:      {{PACKAGE_MANAGER}}        e.g., elm
Linter:               {{LINTER}}             e.g., elm-format, elm-review
Formatter:           {{FORMATTER}}          e.g., elm-format

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use elm-test for testing
- Test decoder functions
- Test update functions
- Test pure functions

##### Property Tests
- Use fuzz testing with elm-test

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., elm-test
Fuzz tool:      {{FUZZ_TOOL}}            e.g., elm-test (built-in)
Coverage tool:  {{COVERAGE_TOOL}}              e.g., elm-coverage

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
