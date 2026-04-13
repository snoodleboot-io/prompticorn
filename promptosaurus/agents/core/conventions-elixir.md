<!-- path: promptosaurus/prompts/agents/core/core-conventions-elixir.md -->
# Core Conventions Elixir

Language:             {{ language }} e.g., Elixir 1.15+
Runtime:              {{ runtime }} e.g., OTP 26
Package Manager:      {{ package_manager }} e.g., mix
Linter:               {{ linter }} e.g., Credo, Sobelow
Formatter:           {{ formatter }} e.g., mix format

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase (Modules)
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

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
Line:           [Template variable]          e.g., 80%
Branch:         [Template variable]        e.g., 70%
Function:       [Template variable]       e.g., 90%
Statement:      [Template variable]      e.g., 85%
Path:           [Template variable]           e.g., 60%

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
Framework:       [Template variable]        e.g., ExUnit
Mocking:        [Template variable]              e.g., Mox
Property tool:   [Template variable]        e.g., PropCheck, StreamData
Coverage tool:  [Template variable]              e.g., ExCoveralls

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
