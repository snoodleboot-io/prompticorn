## Steps

Work through these in order for each documented unit. The order matters: a reader
decides whether to keep reading from the purpose line, so an accurate one-sentence
purpose is worth more than an exhaustive parameter table.

### Step 1: Purpose — what it does in one sentence (not how)

State what the caller gets, in the caller's vocabulary.

- Describe the outcome, not the implementation. "Returns the customer's active
  subscription" — not "queries the subscriptions table and filters by status".
- One sentence. If it needs two, the unit probably does two things.
- Do not restate the name. "get_user() gets a user" tells a reader nothing they
  did not already know from the signature.
- Name the *why* when the unit exists for a non-obvious reason — that is the part
  the code cannot express.

### Step 2: Parameters — name, type, required/optional, constraints

Document what the type signature cannot express.

For each parameter: name, type, required or optional (with the default), and any
constraint that is not visible in the type — valid ranges, mutually exclusive
combinations, units, format, ownership.

```
timeout_ms: int, optional, default 5000
    Must be > 0. Applies per attempt, not to the call as a whole.
region: str, required
    One of the ISO codes in SUPPORTED_REGIONS. Case-insensitive.
```

Units and per-attempt-versus-total semantics are the two most commonly omitted
facts and the two most commonly misused.

### Step 3: Return value — type, shape, possible values

State the type, the shape, and what the values mean.

- For collections: can it be empty, and is the order significant or incidental?
- For optional returns: what does `None` or a null actually signify — not found,
  not permitted, or not yet computed? These need different caller handling.
- For structured returns: document the fields a caller depends on, and say which
  fields are guaranteed present versus conditional.

### Step 4: Errors — what can go wrong and under what conditions

List each error the caller can reasonably be expected to handle, with the condition
that raises it.

- Pair every error with its trigger. "Raises `ValidationError`" is unactionable;
  "raises `ValidationError` when `region` is not in `SUPPORTED_REGIONS`" is.
- Distinguish retryable from terminal — this is the single most useful thing an
  error section can convey.
- Include errors that propagate from dependencies if the caller must handle them.
- Do not document internal errors the caller cannot act on.

### Step 5: Example — at least one realistic usage

Show the call in context, with plausible values.

- Realistic values, not `foo`/`bar` — the example is often the only part read.
- Runnable as written: include the imports and setup a reader would otherwise guess at.
- Show the common case first. Add a second example only for a genuinely different
  mode of use, not for a different parameter value.
- If the unit is easy to misuse, show the correct form next to the tempting wrong one.

### Step 6: Side effects — DB writes, external calls, state changes

State anything that happens beyond returning a value.

- Writes, external calls, cache invalidation, file or queue operations, mutation of
  arguments, global or module-level state changes.
- Say whether the operation is idempotent, and whether it is safe to retry — callers
  need both to write correct error handling.
- Note transactional behaviour: does a partial failure leave partial writes?
- "No side effects" is worth stating explicitly. Silence reads as unknown, and a
  reader who cannot tell will assume the unsafe case.