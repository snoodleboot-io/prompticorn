# Elixir Conventions

Language:             {{LANGUAGE}}           e.g., Elixir 1.15+
Runtime:              {{RUNTIME}}            e.g., OTP 26
Package Manager:      {{PACKAGE_MANAGER}}        e.g., mix
Linter:               {{LINTER}}             e.g., Credo, Sobelow
Formatter:           {{FORMATTER}}          e.g., mix format

## Elixir-Specific Rules

### Error Handling
- Use proper Elixir error handling (try/rescue, with)
- Use tuples {:ok, result} / {:error, reason} for fallible operations
- Raise with `raise/1` only for truly exceptional conditions
- Use DefStruct for structured data

### Concurrency
- Use GenServer for stateful processes
- Use Task for async operations
- Use OTP principles (supervisors, applications)
- Avoid shared mutable state

### Code Style
- Follow Elixir style guide (use mix format)
- Use pipe operator (|>) for readability
- Pattern match in function heads
- Use guards when appropriate

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use ExUnit for testing
- Test one function in isolation
- Use mocks with Mox

##### Integration Tests
- Test at module/application boundary
- Use sandbox mode for database tests
- Test GenServer interactions

##### Property Tests
- Use PropCheck for property-based testing

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., ExUnit
Mocking:        {{MOCKING_LIBRARY}}              e.g., Mox
Property tool:   {{PROPERTY_TOOL}}        e.g., PropCheck, StreamData
Coverage tool:  {{COVERAGE_TOOL}}              e.g., ExCoveralls

#### Scaffolding

```bash
# Run tests
mix test                    # Run tests
mix test --cover           # With coverage
mix test --trace           # Detailed output

# With PropCheck
mix deps.get
mix test --only property

# Configuration (mix.exs)
def project do
  [
    app: :my_app,
    test_coverage: [tool: ExCoveralls],
    deps: deps()
  ]
end
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: |
    mix deps.get
    mix test --cover
```
