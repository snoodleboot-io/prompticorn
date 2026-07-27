# Go Error Handling And Interfaces (Verbose)

## Core Patterns

### Explicit Error Returns

Go has no exceptions for ordinary failures. A function that can fail returns an
`error` as its last value, and the caller checks it immediately. This makes every
failure path visible in the source rather than hidden in a stack unwind.

```go
func writeReport(path string, r Report) error {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    defer f.Close() // runs on every return path below

    if err := json.NewEncoder(f).Encode(r); err != nil {
        return err
    }
    return nil
}
```

The convention is `if err != nil { return ... }` right after the call. When an
error is returned, other results must be assumed unusable — return their zero
values (`nil`, `0`, `""`) alongside the error, and never read them when `err` is
non-nil.

### Wrapping With %w

Context turns a bare `permission denied` into a diagnosable
`writeReport: creating /var/out.json: permission denied`. Wrap with
`fmt.Errorf` and the `%w` verb, which keeps the underlying error inspectable.

```go
func saveReport(id string, r Report) error {
    path := filepath.Join(outDir, id+".json")
    if err := writeReport(path, r); err != nil {
        return fmt.Errorf("saveReport %s: %w", id, err) // %w preserves the cause
    }
    return nil
}
```

Use `%w` when the caller might want to inspect or match the wrapped error, and
`%v` only when you deliberately want to obscure it (e.g. hiding internal details at
a trust boundary). Add one clause of context per layer; do not prefix every
message with "failed to" — the `err != nil` already means failure.

### Inspecting the Chain: errors.Is and errors.As

Because `%w` builds a chain, you inspect it with the `errors` helpers rather than
`==` or type assertions, which only see the outermost error.

```go
u, err := repo.Load(ctx, id)

// errors.Is — does the chain contain this sentinel value?
if errors.Is(err, ErrNotFound) {
    return respond(http.StatusNotFound, "user missing")
}

// errors.As — is there an error of this type anywhere in the chain?
var vErr *ValidationError
if errors.As(err, &vErr) {
    return respond(http.StatusBadRequest, vErr.Field+": "+vErr.Msg)
}
```

`errors.Is` walks the chain comparing against a sentinel; `errors.As` walks it
looking for a value assignable to the target pointer, then assigns it. Both
respect `Unwrap`, so they see through every `%w` layer.

### Sentinel vs. Typed Errors

Two ways to expose a distinguishable error, chosen by what the caller needs.

A **sentinel** is a package-level `error` value for a condition callers only need
to recognize:

```go
var (
    ErrNotFound   = errors.New("not found")
    ErrPermission = errors.New("permission denied")
)

func (r *Repo) Load(id string) (*User, error) {
    row, ok := r.rows[id]
    if !ok {
        return nil, fmt.Errorf("repo load %s: %w", id, ErrNotFound)
    }
    return row, nil
}
```

A **typed error** carries structured data the caller reads after extraction:

```go
type HTTPError struct {
    Status int
    URL    string
    Err    error
}

func (e *HTTPError) Error() string {
    return fmt.Sprintf("%s -> %d: %v", e.URL, e.Status, e.Err)
}

// Implementing Unwrap lets errors.Is/As see through to the cause.
func (e *HTTPError) Unwrap() error { return e.Err }
```

Prefer sentinels for simple "which condition" checks and typed errors when the
caller needs fields (a status code, a field name, a retry-after). Both should be
wrapped with `%w` as they propagate so the chain stays intact.

### Small Interfaces

Go interfaces are satisfied implicitly — any type with the right methods qualifies,
no `implements` keyword. This makes small interfaces enormously flexible. The
standard library's `io.Reader` and `io.Writer` are single-method interfaces that
compose across the entire ecosystem.

```go
// One method: trivial to implement, trivial to fake in a test.
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

type Service struct {
    store UserStore
}

func (s *Service) Greeting(ctx context.Context, id string) (string, error) {
    u, err := s.store.GetUser(ctx, id)
    if err != nil {
        return "", fmt.Errorf("greeting %s: %w", id, err)
    }
    return "Hello, " + u.Name, nil
}
```

The rule of thumb: the bigger the interface, the weaker the abstraction. Keep them
to one or a few methods, and split large ones so consumers depend only on what
they call.

### Accept Interfaces, Return Structs

Take interfaces as parameters so callers can substitute any implementation
(including a test fake). Return concrete structs so callers get the full, typed API
and you avoid inventing an abstraction before you need it.

```go
// ✅ Accept an interface — the caller picks the concrete store.
func NewService(store UserStore) *Service {
    return &Service{store: store}
}

// ✅ Return the concrete *Service, not some Servicer interface.
```

Define the interface in the package that *consumes* it, next to the function that
takes it — not in the package that implements it. That inverts the dependency and
keeps implementations free of interfaces invented for one consumer's convenience.

### The Typed-Nil Interface Gotcha

An interface value holds a (type, value) pair. It equals `nil` only when **both**
are nil. Assigning a nil concrete pointer to an interface yields a non-nil
interface, because the type slot is populated. This bites error returns.

```go
type QueryError struct{ msg string }
func (e *QueryError) Error() string { return e.msg }

// ❌ Wrong: err is a *QueryError typed nil, so the returned error is NON-nil.
func query() error {
    var err *QueryError
    if somethingFailed() {
        err = &QueryError{msg: "bad query"}
    }
    return err // when nothing failed, this is (type=*QueryError, value=nil) != nil
}
```

Callers doing `if query() != nil` see a "failure" that has no message content. Fix
by returning the interface type and assigning `nil` explicitly, or by returning
early:

```go
// ✅ Return a literal nil on the success path.
func query() error {
    if somethingFailed() {
        return &QueryError{msg: "bad query"}
    }
    return nil
}
```

## Common Anti-Patterns

❌ **Discarding errors.**
```go
data, _ := os.ReadFile(path) // failure vanishes; data may be nil
```
✅ **Check and return (or log with a stated reason if truly ignorable).**
```go
data, err := os.ReadFile(path)
if err != nil {
    return fmt.Errorf("reading %s: %w", path, err)
}
```

❌ **Wrapping with `%v`, severing the chain.**
```go
return fmt.Errorf("load failed: %v", err) // errors.Is/As can no longer see err
```
✅ **Use `%w` whenever the cause should stay inspectable.**

❌ **Comparing wrapped errors with `==`.**
```go
if err == ErrNotFound { ... } // false once err has been wrapped
```
✅ **`if errors.Is(err, ErrNotFound)`** walks the chain.

❌ **Fat interfaces one type implements, defined beside the implementation.**
```go
type UserStore interface { // 12 methods, only 2 ever mocked
    GetUser(...) (*User, error)
    // ...ten more
}
```
✅ **Narrow interfaces defined in the consumer**, holding only the methods that
consumer actually calls.

❌ **Returning a concrete error pointer type**, inviting the typed-nil bug.
```go
func do() *MyError { ... } // callers comparing to nil get surprised
```
✅ **Return the `error` interface and a literal `nil` on success.**

## Error and Interface Checklist

- [ ] Every returned error is checked immediately with `if err != nil`
- [ ] No error is silently dropped with `_` unless the reason is stated
- [ ] Propagated errors are wrapped with `%w` and one clause of context
- [ ] Error matching uses `errors.Is` (sentinel) and `errors.As` (typed), not `==`
- [ ] Sentinels are used for "which condition"; typed errors when callers need fields
- [ ] Typed errors implement `Unwrap` so the chain stays traversable
- [ ] Interfaces are small and defined in the consuming package
- [ ] Constructors accept interfaces and return concrete structs
- [ ] Functions return the `error` interface with literal `nil`, avoiding typed-nil

See `code-review-practices` for reviewing error handling and `go-concurrency-patterns`
for propagating errors and cancellation across goroutines.
