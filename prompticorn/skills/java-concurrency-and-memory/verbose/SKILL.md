# Java Concurrency And Memory (Verbose)

## Core Patterns

### The Java Memory Model And Happens-Before

Threads do not automatically see each other's writes. The compiler, JIT, and CPU
may reorder instructions and cache values in registers, so a write in one thread
can be invisible to another indefinitely. The Java Memory Model defines
*happens-before*: if action A happens-before action B, then A's effects are
visible to B. You get those edges only through synchronization.

Sources of happens-before:
- Unlocking a monitor happens-before every later lock of it (`synchronized`).
- A write to a `volatile` field happens-before every later read of it.
- `Thread.start()` happens-before the started thread's first action.
- A thread's last action happens-before another thread's return from `join()`.
- `java.util.concurrent` structures (queues, latches, `Atomic*`) publish safely.

```java
class Flag {
    private volatile boolean ready = false;   // volatile: writes become visible
    private int data;

    void publish(int v) { data = v; ready = true; }      // data write ordered before ready
    int consume() { while (!ready) { } return data; }    // sees data once ready is true
}
```

Drop the `volatile` and the reader may spin forever, or read a stale `data`.

### volatile Gives Visibility, Not Atomicity

`volatile` guarantees visibility and ordering, but not atomic compound operations.
`count++` is read-modify-write: two threads can read the same value and both
increment to the same result, losing an update. Use an atomic for that.

```java
private final AtomicLong hits = new AtomicLong();
hits.incrementAndGet();                       // atomic RMW

// compare-and-set for conditional updates
long cur;
do { cur = hits.get(); } while (!hits.compareAndSet(cur, cur + delta));
```

### final Fields And Safe Publication

A properly constructed immutable object (all fields `final`, no `this` escaping
the constructor) is safe to share across threads with no further synchronization —
the JMM guarantees other threads see the fully initialized `final` fields.
Immutability is the cheapest correct concurrency strategy.

### Executors Instead Of Raw Threads

Creating a thread per task is expensive and unbounded. An executor pools and
reuses threads and hands you `Future`s for results.

```java
try (var pool = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors())) {
    List<Future<Integer>> futures = new ArrayList<>();
    for (var task : tasks) futures.add(pool.submit(task::run));
    for (var f : futures) total += f.get();      // blocks until each completes
}   // AutoCloseable (Java 19+) shuts down and awaits termination
```

Size CPU-bound pools near the core count; I/O-bound pools can be larger, but see
virtual threads below.

### Virtual Threads (Project Loom, Java 21)

Virtual threads are lightweight threads scheduled by the JVM onto a small pool of
carrier OS threads. When a virtual thread blocks on I/O, the JVM unmounts it and
frees the carrier, so millions can exist. You write ordinary blocking code and get
the scalability of async without callback-colored APIs.

```java
try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var req : requests) {
        pool.submit(() -> {
            var resp = blockingHttpCall(req);   // blocks the virtual thread, not a carrier
            store(resp);
        });
    }
}
```

Caveats: virtual threads help I/O-bound workloads, not CPU-bound ones (those still
need real cores). Avoid pinning — holding a `synchronized` monitor or a native
call across a blocking point pins the virtual thread to its carrier; prefer
`ReentrantLock` on hot blocking paths.

### Composing Async With CompletableFuture

`CompletableFuture` chains asynchronous stages without blocking, with explicit
error handling.

```java
CompletableFuture<Void> pipeline =
    CompletableFuture.supplyAsync(() -> fetch(id), pool)
        .thenApply(this::parse)                    // transform the result
        .thenCompose(p -> enrichAsync(p))          // flatten a nested future
        .thenAccept(this::store)                   // consume it
        .exceptionally(ex -> { log.error("failed", ex); return null; });

pipeline.join();
```

Use `thenCompose` (not `thenApply`) when the mapping function itself returns a
future, or you end up with `CompletableFuture<CompletableFuture<T>>`.

### Concurrent Collections

Prefer purpose-built concurrent types over externally synchronized ones:
`ConcurrentHashMap` for shared maps, `CopyOnWriteArrayList` for read-mostly lists,
`BlockingQueue` for producer/consumer hand-off. They scale better than wrapping a
plain collection in `synchronized`, and make check-then-act atomic via methods
like `computeIfAbsent`.

### GC, Briefly

Modern collectors (G1 by default, ZGC/Shenandoah for low pause) manage memory
automatically; you rarely tune them before measuring. What matters for
concurrency: allocation is cheap but not free, and object churn drives GC pauses
that look like latency spikes. Reuse and immutability reduce both — but profile
before optimizing.

## Common Anti-Patterns

❌ **Sharing a flag without visibility guarantees**
```java
private boolean stop;                 // reader may never observe the write
public void run() { while (!stop) work(); }
```
✅ **Make it volatile (or use an atomic)**
```java
private volatile boolean stop;
```

❌ **Treating x++ on a shared field as atomic**
```java
private int count;
public void hit() { count++; }        // lost updates under contention
```
✅ **Use an atomic**
```java
private final AtomicInteger count = new AtomicInteger();
public void hit() { count.incrementAndGet(); }
```

❌ **A thread per task**
```java
for (var t : tasks) new Thread(t).start();   // unbounded, no reuse
```
✅ **Submit to an executor (or virtual threads)**
```java
tasks.forEach(pool::submit);
```

❌ **Swallowing InterruptedException**
```java
try { queue.take(); } catch (InterruptedException e) { }   // interruption lost
```
✅ **Restore the interrupt (or propagate)**
```java
try { queue.take(); }
catch (InterruptedException e) { Thread.currentThread().interrupt(); }
```

## Concurrency And Memory Checklist

- [ ] Shared mutable state guarded by a happens-before edge (lock, volatile, j.u.c)
- [ ] `volatile` used for visibility flags; atomics for compound updates
- [ ] Immutable objects with `final` fields preferred for sharing
- [ ] Executors/thread pools used instead of `new Thread()` per task
- [ ] Pools sized to workload; virtual threads for I/O-bound fan-out
- [ ] Virtual threads not used for CPU-bound loops; pinning avoided
- [ ] `CompletableFuture` chains use `thenCompose` for nested futures and handle errors
- [ ] Concurrent collections chosen over externally synchronized ones
- [ ] `InterruptedException` restores the interrupt flag, never swallowed
- [ ] Lock acquisition order kept consistent to avoid deadlock
