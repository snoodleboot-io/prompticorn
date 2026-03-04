<!-- path: promptosaurus/prompts/core-conventions-go.md -->
# Go Conventions

Language:             {{LANGUAGE}}           e.g., Go 1.22
Runtime:              {{RUNTIME}}            e.g., Go runtime
Package Manager:      {{PACKAGE_MANAGER}}        e.g., go mod
Linter:               {{LINTER}}             e.g., golangci-lint
Formatter:           {{FORMATTER}}          e.g., gofmt, goimports

## Go-Specific Rules

### Error Handling
- Always return `(T, error)` — never panic in library code
- Wrap errors with `fmt.Errorf("context: %w", err)` for adding context
- Use sentinel errors (`var ErrNotFound = errors.New("not found")`) for known conditions
- Handle errors at the boundary — don't defer error handling deep in the stack

### Context
- Use `context.Context` as the first argument on all I/O functions
- Pass context through — don't store it in structs
- Use `context.WithTimeout` or `context.WithCancel` for resource management

### Imports
- Use `goimports` or IDE to manage import groups automatically
- Group: standard library → external packages → internal packages
- Use aliases only when necessary (e.g., `errs "errors"`)

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
- One function or method in isolation
- Use table-driven tests with `testing.T.Run`
- Use `testify/assert` and `testify/require` for assertions
- Create test files alongside source: `foo.go` → `foo_test.go`
- Use `t.Cleanup` for resource teardown

##### Integration Tests
- Test at service or module boundary
- Use test databases (testcontainers-go) or in-memory alternatives
- Test HTTP handlers, database queries, gRPC services

##### E2E Tests
- Use Go's testing framework with external tools
- Test critical user flows with real services

##### Fuzz Tests
- Use `go-fuzz` or built-in fuzzing in Go 1.18+
- Test input validation and parsing functions

##### Mutation Tests
- Use `go-mutesting` to verify test quality
- Run after unit tests pass

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., Go test
Mocking library: {{MOCKING_LIBRARY}}              e.g., testify, gomock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., go test -cover, gocov
Fuzz tool:      {{FUZZ_TOOL}}             e.g., go-fuzz, testing/fuzz

#### Scaffolding

```bash
# Install
go get -u github.com/stretchr/testify
go get -u github.com/testcontainers/testcontainers-go
go install github.com/go-fuzz/go-fuzz-build@latest

# Run tests
go test -v ./...                 # Run all tests
go test -v -cover ./...          # With coverage
go test -v -coverprofile=coverage.out ./...
go tool cover -func=coverage.out # View coverage

# Fuzzing
go test -fuzz=FuzzMyFunction -fuzztime=30s

# Mutation testing
go install github.com/go-mutesting/go-mutesting@latest
go-mutesting ./...
```

##### CI Integration
```yaml
# GitHub Actions example
- name: Run tests
  run: |
    go test -v -coverprofile=coverage.out ./...
    go tool cover -func=coverage.out

- name: Fuzz tests
  run: |
    go test -fuzz=Fuzz -fuzztime=60s ./...
```

### Code Style
- Follow Go idioms — use `go fmt` / `gofmt`
- Use `go vet` and `golangci-lint` in CI
- Keep functions short — one thing per function
- Use interfaces for abstraction, not concrete types
- Prefer value receivers unless you need pointer receivers

### Project Structure
- Use standard Go layout (cmd/, internal/, pkg/)
- Keep `main.go` minimal — delegate to library code
- Use `internal/` for private packages
