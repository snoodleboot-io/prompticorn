# Java Concurrency And Memory (Minimal)

## Purpose
Share data between threads correctly: establish happens-before, prefer pools and
higher-level constructs over raw threads, and know where virtual threads fit.

## Core Techniques

### 1. Happens-Before Or It's A Data Race
Without a happens-before edge, one thread may never see another's write — the JIT
and CPU may reorder and cache freely. `synchronized`, `volatile`, and
`java.util.concurrent` types create those edges.
```java
// ❌ writer sets ready=true, reader may loop forever on a stale cache
boolean ready;              // not volatile
// ✅ volatile establishes visibility + ordering
volatile boolean ready;
```

### 2. volatile For Visibility, Not Atomicity
`volatile` guarantees other threads see the latest write, but `count++` is still
read-modify-write and races. Use `AtomicInteger` (or a lock) for compound updates.
```java
private final AtomicInteger count = new AtomicInteger();
count.incrementAndGet();    // atomic
```

### 3. Use An Executor, Not new Thread()
A thread pool bounds resource use and reuses threads. Submit tasks; get `Future`s.
```java
try (var pool = Executors.newFixedThreadPool(8)) {
    Future<Integer> f = pool.submit(() -> compute());
    int r = f.get();
}   // try-with-resources shuts the pool down (Java 19+)
```

### 4. Virtual Threads For Blocking I/O (Loom)
Virtual threads (Java 21) are cheap — millions can exist. A blocking call parks
the virtual thread and frees the carrier OS thread. Write plain blocking code; get
scalability.
```java
try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
    pool.submit(() -> handle(request));   // one virtual thread per task
}
```
Use them for I/O-bound work, not CPU-bound loops (those still need real cores).

### 5. Compose Async With CompletableFuture
```java
CompletableFuture
    .supplyAsync(() -> fetch(id), pool)
    .thenApply(this::parse)
    .thenAccept(this::store)
    .exceptionally(ex -> { log(ex); return null; });
```

### 6. Prefer Immutability And Concurrent Collections
Immutable objects are safe to share with no synchronization. When you need shared
mutable state, reach for `ConcurrentHashMap` over a `synchronized` wrapper.

## Warning Signs

- A flag polled across threads without `volatile` or synchronization
- `x++` / check-then-act on a shared field treated as atomic
- `new Thread()` per task instead of a pooled executor
- Virtual threads used for CPU-bound work (no gain, starves carriers)
- `catch (InterruptedException)` that swallows without restoring the interrupt
- Locks acquired in inconsistent order across code paths (deadlock)
