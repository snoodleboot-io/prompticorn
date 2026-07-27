# Go Concurrency Patterns (Verbose)

## Core Patterns

### Goroutines and Channels

A goroutine is a lightweight thread the runtime multiplexes onto OS threads.
Channels are the typed conduits goroutines use to pass values and, crucially,
ownership of data. The guiding maxim is "don't communicate by sharing memory;
share memory by communicating."

```go
// Generate values, hand them off, and signal completion by closing.
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out) // close exactly once, from the sole sender
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

for v := range gen(1, 2, 3) { // range receives until out is closed
    fmt.Println(v)
}
```

Two rules prevent most channel bugs: only the sending side closes a channel, and
a channel is closed exactly once. Receivers detect closure with the two-value
form `v, ok := <-ch` (`ok` is false once drained) or with `range`.

Unbuffered channels are synchronization points — a send blocks until a receive is
ready. Buffered channels (`make(chan T, n)`) decouple sender and receiver up to `n`
queued values; use a buffer to smooth bursts, not as an unbounded queue.

### select and Timeouts

`select` waits on multiple channel operations, proceeding with whichever is ready
first (random choice on ties). It is how a goroutine handles timeouts,
cancellation, and multiple input streams at once.

```go
func waitForResult(ctx context.Context, work <-chan Result) (Result, error) {
    select {
    case r := <-work:
        return r, nil
    case <-ctx.Done():          // cancelled or deadline exceeded
        return Result{}, ctx.Err()
    case <-time.After(5 * time.Second): // local upper bound
        return Result{}, errors.New("timed out")
    }
}
```

A `default` case makes a `select` non-blocking — a best-effort send that must not
stall the hot path:

```go
select {
case metrics <- sample: // deliver if a receiver is ready
default:                 // otherwise drop rather than block
}
```

### context for Cancellation and Deadlines

`context.Context` carries cancellation signals and deadlines across API
boundaries. Pass it as the first argument, propagate it downward, and never store
it in a struct. Cancelling a parent cancels all derived contexts, which is how one
timeout unwinds an entire call tree.

```go
func handleRequest(ctx context.Context, id string) error {
    ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
    defer cancel() // release resources even on the success path

    rows, err := db.QueryContext(ctx, "SELECT ...", id) // honors cancellation
    if err != nil {
        return err
    }
    defer rows.Close()
    return process(ctx, rows)
}
```

Any long-running or blocking loop should select on `ctx.Done()` so it can abandon
work when the caller gives up:

```go
func stream(ctx context.Context, in <-chan Event, out chan<- Event) {
    for {
        select {
        case <-ctx.Done():
            return // stop promptly; no leak
        case e, ok := <-in:
            if !ok {
                return
            }
            out <- transform(e)
        }
    }
}
```

### Goroutine Leaks

A leaked goroutine is one that never returns because it is blocked forever on a
channel operation whose counterpart disappeared. Leaks accumulate memory and can
hold references that prevent GC. Every goroutine needs a guaranteed exit.

```go
// ❌ Leak: the goroutine blocks on send if the caller stops receiving early.
func search(query string) <-chan Result {
    ch := make(chan Result)
    go func() {
        ch <- slowSearch(query) // blocks forever if no one receives
    }()
    return ch
}

// ✅ Fix: a buffer of one guarantees the send completes, or select on ctx.
func search(ctx context.Context, query string) <-chan Result {
    ch := make(chan Result, 1) // send succeeds even if the receiver left
    go func() {
        select {
        case ch <- slowSearch(query):
        case <-ctx.Done(): // abandon delivery if cancelled
        }
    }()
    return ch
}
```

### Worker Pool

A worker pool bounds concurrency to a fixed number of goroutines draining a shared
jobs channel. It prevents the "one goroutine per request" explosion that exhausts
memory or downstream connection limits.

```go
func run(ctx context.Context, jobs []Job, workers int) []Result {
    jobCh := make(chan Job)
    resCh := make(chan Result)

    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := range jobCh { // exits when jobCh is closed
                select {
                case resCh <- process(j):
                case <-ctx.Done():
                    return
                }
            }
        }()
    }

    // Feed jobs, then close so workers' range loops terminate.
    go func() {
        defer close(jobCh)
        for _, j := range jobs {
            select {
            case jobCh <- j:
            case <-ctx.Done():
                return
            }
        }
    }()

    // Close results once every worker has finished sending.
    go func() {
        wg.Wait()
        close(resCh)
    }()

    var out []Result
    for r := range resCh {
        out = append(out, r)
    }
    return out
}
```

### Channels vs. sync Primitives

Both are correct tools; the choice is about which model fits the problem.

| Use channels when... | Use sync.Mutex/RWMutex when... |
|---|---|
| Passing ownership of data between stages | Guarding shared state mutated in place |
| Fan-out / fan-in, pipelines | A counter, cache map, or config struct |
| Signaling events or completion | The critical section is tiny and hot |
| Coordinating goroutine lifecycles | Channel plumbing would obscure intent |

```go
// Mutex fits shared in-place state better than a channel would.
type Cache struct {
    mu sync.RWMutex
    m  map[string]string
}

func (c *Cache) Get(k string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.m[k]
    return v, ok // RWMutex lets concurrent reads proceed; Set would take Lock()
}
```

Use `sync.Once` for exactly-once initialization and `sync.WaitGroup` to wait for a
known set of goroutines. Reach for `atomic` only for simple counters/flags where a
mutex is measurably too costly.

### Data Races and -race

A data race is two goroutines accessing the same memory concurrently with at least
one write and no synchronization. Races are undefined behavior and often invisible
until production load. The race detector finds them:

```
go test -race ./...
```

`-race` instruments every memory access and reports the conflicting stacks. It
carries real overhead (roughly 5-10x), so run it in CI and testing rather than in
production builds. A green suite that never ran under `-race` says nothing about
race freedom.

## Common Anti-Patterns

❌ **Closing a channel from the receiver, or closing it twice** — both panic.
✅ **The sole sender closes, exactly once; use a WaitGroup to know when all senders are done.**

❌ **Forgetting `cancel`** from `WithCancel`/`WithTimeout`, leaking the context's timer.
```go
ctx, _ := context.WithTimeout(parent, time.Second) // cancel discarded
```
✅ **`ctx, cancel := ...; defer cancel()`** every time.

❌ **Unbounded goroutines**, one per request, until the process runs out of memory.
✅ **Bound concurrency with a worker pool or a semaphore channel.**

❌ **Loop variable captured by a goroutine in Go before 1.22**, so every goroutine sees the last value of `v` in `for _, v := range items`.
✅ **Pass it as an argument** — `go func(v Item){ use(v) }(v)` — or rely on Go 1.22+ per-iteration scoping, and confirm your target version.

❌ **Shared map or counter mutated by several goroutines with no synchronization.**
✅ **Guard it with a mutex, or funnel updates through a single owning goroutine via a channel.**

## Concurrency Checklist

- [ ] Every goroutine has a guaranteed exit path (closed channel, `ctx.Done()`, or buffered send)
- [ ] Channels are closed by the sole sender, exactly once — never by a receiver
- [ ] `context.Context` is the first parameter and is propagated down the call tree
- [ ] Every `WithCancel`/`WithTimeout` has a matching `defer cancel()`
- [ ] Blocking loops select on `ctx.Done()` so cancellation is honored promptly
- [ ] Concurrency is bounded (worker pool or semaphore), not one goroutine per unit of work
- [ ] Shared mutable state is guarded by a mutex or owned by a single goroutine
- [ ] `sync.WaitGroup` gates the close of any results channel
- [ ] Tests run under `go test -race` in CI

See `performance-optimization` before tuning pool sizes and `debugging-methodology`
for reproducing intermittent races.
