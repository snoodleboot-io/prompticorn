---
name: "docs"
description: Step-by-step process for docs
steps:
- Purpose — what it does in one sentence (not how)
- Parameters — name, type, required/optional, constraints
- Return value — type, shape, possible values
- Errors — what can go wrong and under what conditions
- Example — at least one realistic usage
- Side effects — DB writes, external calls, state changes
---

## Steps

### Step 1: Purpose — what it does in one sentence (not how)

State the outcome in the caller's vocabulary, not the implementation. One sentence.
Do not restate the name — "get_user() gets a user" says nothing.

### Step 2: Parameters — name, type, required/optional, constraints

Document what the type signature cannot express: valid ranges, units, format,
mutually exclusive combinations, and the default for every optional parameter.
Units and per-attempt-versus-total semantics are the most commonly omitted facts.

### Step 3: Return value — type, shape, possible values

Type, shape, and meaning. Can a collection be empty, and is its order significant?
What does `None` signify — not found, not permitted, or not yet computed? Those
need different caller handling.

### Step 4: Errors — what can go wrong and under what conditions

Pair every error with its trigger; "raises ValidationError" alone is unactionable.
Distinguish retryable from terminal — the most useful thing this section conveys.
Omit internal errors the caller cannot act on.

### Step 5: Example — at least one realistic usage

Realistic values, not `foo`/`bar`, and runnable as written including imports. Show
the common case first. If the unit is easy to misuse, show the correct form beside
the tempting wrong one.

### Step 6: Side effects — DB writes, external calls, state changes

Writes, external calls, cache invalidation, argument mutation, global state. Say
whether it is idempotent and safe to retry, and whether partial failure leaves
partial writes. State "no side effects" explicitly — silence reads as unknown.
