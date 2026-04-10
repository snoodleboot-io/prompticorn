---
name: performance-workflow
description: Step-by-step process for performance
steps:
- N+1 QUERIES — database calls inside loops, missing eager loading
- UNNECESSARY COMPUTATION — work done on every request that could be cached or pre-computed
- MISSING INDEXES — columns filtered, sorted, or joined without an index
- LARGE PAYLOADS — over-fetching data, missing pagination, uncompressed responses
- BLOCKING OPERATIONS — sync I/O in async contexts, long-running work on the main
  thread
- MEMORY LEAKS — unbounded caches, event listeners not cleaned up, large objects held
  in scope
- REDUNDANT NETWORK CALLS — missing batching, no request deduplication, no caching
  headers
- ALGORITHMIC COMPLEXITY — O(n²) or worse where a better algorithm exists
- '**Check for session file:**'
- '**If no session exists:**'
- '**If session exists:**'
- '**During work:**'
- '**On mode switch:**'
---

## Steps

### Step 1: N+1 QUERIES — database calls inside loops, missing eager loading

Detailed instructions for this step.

### Step 2: UNNECESSARY COMPUTATION — work done on every request that could be cached or pre-computed

Detailed instructions for this step.

### Step 3: MISSING INDEXES — columns filtered, sorted, or joined without an index

Detailed instructions for this step.

### Step 4: LARGE PAYLOADS — over-fetching data, missing pagination, uncompressed responses

Detailed instructions for this step.

### Step 5: BLOCKING OPERATIONS — sync I/O in async contexts, long-running work on the main thread

Detailed instructions for this step.

### Step 6: MEMORY LEAKS — unbounded caches, event listeners not cleaned up, large objects held in scope

Detailed instructions for this step.

### Step 7: REDUNDANT NETWORK CALLS — missing batching, no request deduplication, no caching headers

Detailed instructions for this step.

### Step 8: ALGORITHMIC COMPLEXITY — O(n²) or worse where a better algorithm exists

Detailed instructions for this step.

### Step 9: **Check for session file:**

Detailed instructions for this step.

### Step 10: **If no session exists:**

Detailed instructions for this step.

### Step 11: **If session exists:**

Detailed instructions for this step.

### Step 12: **During work:**

Detailed instructions for this step.

### Step 13: **On mode switch:**

Detailed instructions for this step.

