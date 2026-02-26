# Go Conventions

Language:             {{LANGUAGE}}           e.g., Go 1.22
Runtime:              {{RUNTIME}}            e.g., Go runtime
Package Manager:      {{PKG_MANAGER}}        e.g., go mod
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
Framework:            {{TEST_FRAMEWORK}}     e.g., Go test
Coverage target:      {{COVERAGE_%}}         e.g., 80%
Mocking library:     {{MOCK_LIB}}           e.g., testify, gomock

- Use table-driven tests with `testing.T.Run`
- Use `testify/assert` and `testify/require` for assertions
- Create test files alongside source: `foo.go` → `foo_test.go`
- Use `t.Cleanup` for resource teardown

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
