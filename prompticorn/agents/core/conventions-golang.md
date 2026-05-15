<!-- path: prompticorn/prompts/agents/core/core-conventions-golang.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions Golang

Language:             {{ language }} e.g., Go 1.22
Runtime:              {{ runtime }} e.g., Go runtime
Package Manager:      {{ package_manager }} e.g., go mod
Linter:               {{ linter }} e.g., golangci-lint
Formatter:           {{ formatter }} e.g., gofmt, goimports

### Naming Conventions

Files:               snake_case
Variables:          mixedCase (camelCase)
Constants:          MixedCase or UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

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

[Dynamic content - see template]

TODO

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
