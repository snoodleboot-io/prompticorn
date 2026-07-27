# C# Async And LINQ (Verbose)

## Core Patterns

### async/await And The Continuation Model

`await` does not block a thread. It registers the rest of the method as a
continuation, returns control to the caller, and resumes when the awaited task
completes. The thread is free to do other work in the meantime — that is the whole
point of async I/O.

```csharp
public async Task<Order> LoadAsync(int id)
{
    var order = await _db.GetOrderAsync(id);          // thread released while waiting
    order.Lines = await _db.GetLinesAsync(id);        // resumes, awaits again
    return order;
}
```

Make async cascade up the call chain. A single blocking call in the middle
defeats the benefit for everything above it.

### Sync-Over-Async Deadlocks

Blocking on a task with `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` is
the most common async bug. On a captured synchronization context (classic ASP.NET,
WPF, WinForms), the continuation needs the very thread that is now blocked waiting
for it — a deadlock.

```csharp
// ❌ deadlocks under a sync context
public ActionResult Index()
{
    var data = GetDataAsync().Result;   // continuation can't get the UI/request thread
    return View(data);
}

// ✅ await all the way up
public async Task<ActionResult> Index()
{
    var data = await GetDataAsync();
    return View(data);
}
```

### ConfigureAwait(false)

By default a continuation resumes on the captured context. Library code almost
never needs that context, and capturing it invites the deadlock above. Use
`ConfigureAwait(false)` in libraries so the continuation runs on a thread-pool
thread.

```csharp
public async Task<string> FetchAsync(Uri url)
{
    using var resp = await _http.GetAsync(url).ConfigureAwait(false);
    return await resp.Content.ReadAsStringAsync().ConfigureAwait(false);
}
```

Application code on ASP.NET Core has no synchronization context, so it matters
less there; libraries should stay defensive and always add it.

### async void Is A Trap

`async void` cannot be awaited and its exceptions cannot be caught by the caller —
they tear down the process. Use it only for event handlers, which the framework
signature requires; everything else returns `Task`.

```csharp
// ✅ the only acceptable async void
private async void OnClick(object sender, EventArgs e) => await SaveAsync();
```

### Task vs ValueTask

`Task` is a reference type: awaiting one that is already complete still allocates.
`ValueTask` can wrap an already-available result with no allocation — valuable on
hot paths that usually complete synchronously (cache hits). The cost is stricter
rules: await it exactly once, never block on it, never store it in a field.

```csharp
public ValueTask<byte[]> ReadAsync(string key)
{
    if (_cache.TryGetValue(key, out var cached))
        return new ValueTask<byte[]>(cached);      // synchronous, zero allocation
    return new ValueTask<byte[]>(LoadFromDiskAsync(key));
}
```

Default to `Task`; reach for `ValueTask` only when profiling shows the allocation
matters.

### LINQ Deferred Execution

Most LINQ operators (`Where`, `Select`, `OrderBy`, `Take`) are lazy: they build a
pipeline and execute only when enumerated. Enumeration happens on `foreach`, or on
a materializing operator (`ToList`, `ToArray`, `Count`, `First`, `Any`, `Sum`).

```csharp
var query = orders.Where(o => o.Total > 100);   // no work done here

foreach (var o in query) { /* ... */ }          // executed now
var count = query.Count();                        // executed AGAIN — second pass
```

### The Multiple-Enumeration Trap

Because the query is re-evaluated each time it is enumerated, holding an
`IEnumerable` and iterating it twice runs the pipeline twice — and against
`IQueryable`, that is two database round-trips.

```csharp
// ❌ two full evaluations
IEnumerable<Order> big = db.Orders.Where(o => o.Total > 100);
if (big.Any())                    // round-trip 1
    Process(big.First());         // round-trip 2

// ✅ materialize once, reuse
var list = db.Orders.Where(o => o.Total > 100).ToList();
if (list.Count > 0)
    Process(list[0]);
```

### IEnumerable vs IQueryable

`IQueryable<T>` captures the query as an expression tree that the provider (EF
Core) translates to SQL, so filtering and paging run in the database. The moment
you switch to `IEnumerable<T>` — via `AsEnumerable()`, `ToList()`, or a method the
provider cannot translate — subsequent operators run in memory over rows already
fetched.

```csharp
// ✅ WHERE + ORDER BY + TOP run in SQL; one small result set returns
var top = db.Orders
            .Where(o => o.Total > 100)
            .OrderByDescending(o => o.Total)
            .Take(10)
            .ToList();

// ❌ pulls the entire table into memory, then filters client-side
var bad = db.Orders.AsEnumerable()
            .Where(o => o.Total > 100)
            .ToList();
```

## Common Anti-Patterns

❌ **Blocking on async**
```csharp
var user = _svc.GetUserAsync(id).Result;   // deadlock risk, thread starvation
```
✅ **Await it**
```csharp
var user = await _svc.GetUserAsync(id);
```

❌ **async void beyond event handlers**
```csharp
public async void ProcessQueue() => await DrainAsync();  // unobservable exceptions
```
✅ **Return Task**
```csharp
public async Task ProcessQueueAsync() => await DrainAsync();
```

❌ **Enumerating a deferred query repeatedly**
```csharp
var q = db.Orders.Where(o => o.Open);
var n = q.Count(); var first = q.First();   // two queries
```
✅ **Materialize once**
```csharp
var open = db.Orders.Where(o => o.Open).ToList();
```

❌ **Filtering after leaving IQueryable**
```csharp
db.Orders.ToList().Where(o => o.Total > 100);   // whole table loaded first
```
✅ **Filter in the query**
```csharp
db.Orders.Where(o => o.Total > 100).ToList();
```

## Async And LINQ Checklist

- [ ] async cascades up the chain; no `.Result` / `.Wait()` on async code
- [ ] `ConfigureAwait(false)` on awaits in library code
- [ ] `async void` only on event handlers
- [ ] `Task` the default; `ValueTask` only where profiling justifies it, awaited once
- [ ] Deferred queries materialized once before multiple use
- [ ] Filtering/paging kept in `IQueryable` so it runs in SQL
- [ ] `AsEnumerable()` / `ToList()` placed deliberately, not accidentally early
- [ ] `CancellationToken` accepted and passed through async APIs
