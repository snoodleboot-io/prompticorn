# Go Concurrency Patterns (Minimal)

## Purpose
Coordinate goroutines with channels and `context`, and choose channels vs. mutexes so concurrent code stays correct and leak-free.

## Core Techniques

### 1. Goroutines Communicate Over Channels
```go
func producer(out chan<- int) {
    for i := 0; i < 3; i++ {
        out <- i
    }
    close(out) // signals "no more values" to the range loop
}

ch := make(chan int)
go producer(ch)
for v := range ch { // ranges until ch is closed
    fmt.Println(v)
}
```
The sender owns the channel and is the only one that closes it. Closing tells every receiver the stream is done; sending on a closed channel panics.

### 2. select Multiplexes and Times Out
```go
select {
case v := <-work:
    handle(v)
case <-time.After(2 * time.Second):
    return errTimeout
case <-done:
    return nil
}
```
`select` blocks until one case is ready; if several are ready it picks one at random. Add a `default:` to make it non-blocking. `time.After` gives a per-select timeout without an extra goroutine.

### 3. context for Cancellation and Deadlines
```go
func fetch(ctx context.Context, url string) (*http.Response, error) {
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    return http.DefaultClient.Do(req) // aborts if ctx is cancelled or times out
}

ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel() // ALWAYS call cancel to release the timer
```
Pass `ctx` as the first parameter down the call tree. Select on `ctx.Done()` in any loop that could otherwise run forever, and check `ctx.Err()` for the reason.

### 4. Don't Leak Goroutines
```go
// ❌ Leaks: on an unbuffered channel, if the caller stops receiving early,
//    this goroutine blocks on the send forever.
func leaky() <-chan int {
    ch := make(chan int)
    go func() { ch <- expensive() }()
    return ch
}

// ✅ A buffer of 1 guarantees the send completes even if the receiver left.
func safe() <-chan int {
    ch := make(chan int, 1)
    go func() { ch <- expensive() }()
    return ch
}
```
Every goroutine you start must have a guaranteed path to completion — a buffered send, a closed channel, or a `select` on `ctx.Done()`. The classic leak is a goroutine blocked forever because its counterpart went away.

### 5. Worker Pool With WaitGroup
```go
func pool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := range jobs { // exits when jobs is closed
                results <- process(j)
            }
        }()
    }
    wg.Wait()      // all workers have drained jobs
    close(results) // safe to close only after every sender is done
}
```
A fixed worker count bounds concurrency. Close `jobs` to signal workers to stop; close `results` only after `wg.Wait()`.

### 6. Channels vs. Mutex
"Share memory by communicating" — pass ownership of data through a channel so only one goroutine touches it at a time. Reach for `sync.Mutex` when the natural model is shared state guarded in place (a counter, a cache map), where channel plumbing would only obscure intent. Both are correct tools; pick the one that fits the problem.

### 7. Detect Races With -race
```
go test -race ./...
```
The race detector instruments memory access and reports concurrent unsynchronized read/write. Run it in CI; a passing test without `-race` proves nothing about data races.

## Warning Signs

- A goroutine that can block forever on a send/receive with no `ctx.Done()` or buffer escape
- `context.WithTimeout`/`WithCancel` whose `cancel` is never called (`go vet` flags this)
- Closing a channel from the receiver side, or closing it more than once
- Shared variables read and written by multiple goroutines with no mutex or channel
- Unbounded goroutine creation (one per request with no pool) under load
- Trusting tests that never ran under `-race`
