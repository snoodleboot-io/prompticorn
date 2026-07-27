# C# Async And LINQ (Minimal)

## Purpose
Write async code that doesn't deadlock, and LINQ queries that run once, in the
right place (in memory vs. in the database).

## Core Techniques

### 1. async All The Way — Never Block On Async
Blocking on a Task with `.Result` or `.Wait()` deadlocks when a captured
synchronization context is waiting for the same thread.
```csharp
// ❌ classic deadlock in UI / legacy ASP.NET
var data = FetchAsync().Result;

// ✅ await up the call chain
var data = await FetchAsync();
```

### 2. ConfigureAwait(false) In Libraries
By default a continuation resumes on the captured context. Library code rarely
needs it; `ConfigureAwait(false)` resumes on any thread-pool thread and avoids
context-capture deadlocks.
```csharp
var bytes = await http.GetByteArrayAsync(url).ConfigureAwait(false);
```

### 3. Task vs ValueTask
`Task` is the default. `ValueTask` avoids an allocation when a method usually
completes synchronously (e.g. a cache hit) — but you must await it exactly once
and never block on it.
```csharp
public ValueTask<int> GetAsync(string k) =>
    _cache.TryGetValue(k, out var v) ? new ValueTask<int>(v) : LoadAsync(k);
```

### 4. LINQ Is Deferred
A query describes work; it runs only when enumerated (`foreach`, `ToList`,
`Count`, `First`). Building a query does not touch data.
```csharp
var q = numbers.Where(n => n > 10);   // nothing executed yet
var list = q.ToList();                // executes now
```

### 5. Beware Multiple Enumeration
Each enumeration re-runs the whole pipeline. Iterating a deferred query twice
means two passes — or two database round-trips.
```csharp
// ❌ query runs twice
if (q.Any()) return q.First();
// ✅ materialize once
var items = q.ToList();
if (items.Count > 0) return items[0];
```

### 6. IEnumerable vs IQueryable
`IQueryable` builds an expression tree the provider translates to SQL — filtering
happens in the database. Switching to `IEnumerable` (or calling `AsEnumerable()`)
pulls rows into memory first, then filters client-side.
```csharp
// ✅ WHERE runs in SQL
db.Orders.Where(o => o.Total > 100);
// ❌ loads every row, then filters in C#
db.Orders.AsEnumerable().Where(o => o.Total > 100);
```

## Warning Signs

- `.Result` / `.Wait()` / `.GetAwaiter().GetResult()` on async code
- `async void` on anything but an event handler (exceptions escape unobservable)
- A deferred query enumerated more than once (repeated DB hits)
- `AsEnumerable()` / `ToList()` called early, then filtering in memory
- `ValueTask` awaited twice or stored in a field
- Missing `ConfigureAwait(false)` in a shared library

See the general-practice conventions for broader code-quality guidance.
