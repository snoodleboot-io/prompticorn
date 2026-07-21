# Problem Decomposition (Minimal)

## Purpose
Turn a vague request into a tree of sub-problems that are individually measurable, independently solvable, and small enough to finish.

## Core Techniques

### 1. Worked Example: "Make Search Faster"
The request is unfalsifiable as stated. Decompose until every leaf has a number.

```
"Make search faster"
│
├── Q: faster for whom? → p95 latency for logged-in users on /search
│      Baseline: p95 = 3.2s. Target: p95 < 800ms.
│
├── A. Where does the 3.2s go?  [SPIKE — 1 day, do this first]
│      Measured: 210ms app → 2.6s query → 180ms render → 210ms network
│      → 81% is the query. B and C are now known low-value.
│
├── B. Query time (2.6s)                      ← owns the outcome
│    ├── B1. `search_index` has no trigram index on `title` (Seq Scan)
│    │       Measurable: EXPLAIN shows Index Scan; query < 400ms
│    ├── B2. Result count is unbounded; p99 fetches 40k rows
│    │       Measurable: LIMIT 50 + keyset paging; rows fetched < 100
│    └── B3. Facet counts recomputed per request
│            Measurable: 5-min cache; facet cost < 20ms
│
├── C. Render (180ms)   — cap: even at 0ms, target is missed. Defer.
└── D. Network (210ms)  — cap: same. Defer.
```

Two rules made this useful: the spike ran before any estimating, and each leaf
names the measurement that proves it done.

### 2. Work Backwards From the Output
Start at the artifact you must produce and ask what must exist immediately
before it. "A ranked list of 50 results" ← "a scored candidate set" ← "a
retrieved candidate set" ← "an index". Each arrow is a seam.

### 3. Find the Seam
A good split point is an existing or plausible interface — a function
signature, a queue, a table, an HTTP contract. If you can write down the
type that crosses the boundary, two people can work on opposite sides. If you
cannot, you have drawn the line in the wrong place.

### 4. Vertical Slice, Not Horizontal Layer
```
❌ Horizontal: week 1 all schemas, week 2 all services, week 3 all endpoints
   → nothing works until week 3; every integration risk lands at the end

✅ Vertical: one narrow end-to-end path (one search field, no facets, no
   paging) through every layer, then widen
   → the risky integration is proven on day 3
```

### 5. Spike the Unknown First
Order sub-problems by uncertainty, not by dependency or by ease. Timebox the
spike (1-2 days), and state the question it answers: "Can Postgres trigram
search hit 400ms at our row count?" A spike that produces an answer but no
number has failed.

### 6. Ask "What Would Have To Be True?"
For any proposed plan, list the conditions required for it to work, then check
the cheapest and least certain one first. "Caching facets works *if* facet
values change less than once per 5 minutes." Query the write rate. Ten minutes,
and you keep or discard B3 on evidence.

## Warning Signs

- A sub-problem with no measurable done condition ("improve the query layer")
- "Independent" parts that touch the same table, lock, or migration
- Every branch estimated before anything was measured
- The tree is one level deep — that is a list, not a decomposition
- A leaf still too big to finish in a day
- All slices horizontal, integration deferred to the end
- Nobody can say which sub-problem, if solved alone, moves the metric
