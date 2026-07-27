# Go Error Handling And Interfaces (Minimal)

## Purpose
Return errors explicitly, wrap them to preserve context and cause, and design small interfaces that keep dependencies loose.

## Core Techniques

### 1. Return Errors, Check Them Immediately
```go
func readConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err // handle the failure here, not three layers up
    }
    return parse(data)
}
```
Errors are ordinary values, returned as the last result. Check `if err != nil` right after the call. Return a nil `*Config` alongside a non-nil error — callers must not read the first value when the error is set.

### 2. Wrap With %w to Preserve the Chain
```go
func loadUser(id string) (*User, error) {
    u, err := db.Fetch(id)
    if err != nil {
        return nil, fmt.Errorf("loadUser %s: %w", id, err) // %w keeps err inspectable
    }
    return u, nil
}
```
`%w` wraps the underlying error so it stays reachable via `errors.Is`/`errors.As`; `%v` would flatten it to a string and lose the cause. Add context (what you were doing) at each layer, but don't repeat "failed to" everywhere.

### 3. Inspect With errors.Is and errors.As
```go
_, err := loadUser("42")

if errors.Is(err, sql.ErrNoRows) { // matches anywhere in the wrap chain
    return http.StatusNotFound
}

var pathErr *os.PathError
if errors.As(err, &pathErr) { // extracts a typed error from the chain
    log.Printf("bad path: %s", pathErr.Path)
}
```
`errors.Is` compares against a sentinel value; `errors.As` unwraps into a typed target so you can read its fields. Both walk the whole `%w` chain.

### 4. Sentinel vs. Typed Errors
```go
// Sentinel: a fixed, comparable value for a well-known condition.
var ErrNotFound = errors.New("not found")

// Typed: carries structured data the caller can read.
type ValidationError struct {
    Field string
    Msg   string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Msg)
}
```
Use a sentinel when callers only need to ask "is it this?" (`errors.Is`). Use a typed error when they need details (`errors.As`, then read fields).

### 5. Small Interfaces; Accept Interfaces, Return Structs
```go
// Small interface — one method, easy to implement and mock.
type Store interface {
    Get(id string) (*User, error)
}

// Accept the interface (loose coupling), return the concrete type.
func NewService(s Store) *Service {
    return &Service{store: s}
}
```
The narrower the interface, the more types satisfy it and the easier it is to test. Define interfaces in the consuming package, not next to the implementation. Return concrete structs so callers see the full API and you avoid premature abstraction.

### 6. The Typed-Nil Interface Gotcha
```go
type MyError struct{}
func (e *MyError) Error() string { return "boom" }

func doWork() error {
    var e *MyError = nil // concrete pointer, nil value
    return e             // ❌ returns a NON-nil interface wrapping a nil pointer
}

if doWork() != nil {
    // this fires! the interface holds (type=*MyError, value=nil) != nil
}
```
An interface is nil only when both its type and value are nil. Returning a typed nil pointer produces a non-nil `error`. Fix: return a literal `nil`, or only assign the error variable when there actually is an error.

## Warning Signs

- Ignored errors: `data, _ := os.ReadFile(path)` on anything that can genuinely fail
- Wrapping with `%v` instead of `%w`, breaking `errors.Is`/`errors.As`
- Comparing errors with `err == ErrFoo` instead of `errors.Is` when wrapping is in play
- Large "kitchen-sink" interfaces that only one concrete type will ever implement
- Interfaces defined in the producer package and returned from constructors
- Functions returning a concrete error pointer type instead of `error` (invites the typed-nil bug)
