<!-- path: flat/review-performance.md -->
# review-performance.md
# Behavior when the user asks for a performance review or audit.

When the user asks to review code for performance, audit for bottlenecks,
or diagnose a slowness issue:

Review specifically for:

1. N+1 QUERIES — database calls inside loops, missing eager loading
2. UNNECESSARY COMPUTATION — work done on every request that could be cached or pre-computed
3. MISSING INDEXES — columns filtered, sorted, or joined without an index
4. LARGE PAYLOADS — over-fetching data, missing pagination, uncompressed responses
5. BLOCKING OPERATIONS — sync I/O in async contexts, long-running work on the main thread
6. MEMORY LEAKS — unbounded caches, event listeners not cleaned up, large objects held in scope
7. REDUNDANT NETWORK CALLS — missing batching, no request deduplication, no caching headers
8. ALGORITHMIC COMPLEXITY — O(n²) or worse where a better algorithm exists

For each issue:
- Location (file and function name)
- What the problem is and why it matters at scale
- Suggested fix with estimated impact: HIGH / MEDIUM / LOW

Skip issues that only matter at scale unlikely to be reached — state that assumption explicitly.

If the user has not provided expected load or scale context, ask before reviewing.

For database queries specifically, also check:
- Full table scans
- SELECT * where specific columns would suffice
- Transactions held open longer than needed
- Missing query result limits
