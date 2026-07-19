<!-- path: prompticorn/prompts/agents/core/core-conventions-elixir.md -->
# Core Conventions Elixir

Language:             {{ language or "e.g., Elixir 1.15+" }}
Runtime:              {{ runtime or "e.g., OTP 26" }}
Package Manager:      {{ package_manager or "e.g., mix" }}
Linter:               {{ linter or "e.g., Credo, Sobelow" }}
Formatter:           {{ formatter or "e.g., mix format" }}

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
Line:           {{ coverage_targets.get('line', '') or "e.g., 80%" }}
Branch:         {{ coverage_targets.get('branch', '') or "e.g., 70%" }}
Function:       {{ coverage_targets.get('function', '') or "e.g., 90%" }}
Statement:      {{ coverage_targets.get('statement', '') or "e.g., 85%" }}
Path:           {{ coverage_targets.get('path', '') or "e.g., 60%" }}

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
Framework:       {{ test_framework or "e.g., ExUnit" }}
Mocking:        {{ mocking_library or "e.g., Mox" }}
Property tool:           e.g., PropCheck, StreamData
Coverage tool:  {{ coverage_tool or "e.g., ExCoveralls" }}

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
