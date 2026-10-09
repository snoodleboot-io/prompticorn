# Agent Tool Design (Minimal)

## Purpose
Design the tool surface an agent acts through so the model picks the right tool,
recovers from its own mistakes, and terminates — without unbounded cost or
duplicated side effects.

## Core Techniques

### 1. Write the Description for the Caller, Not the Implementer
Most agent failures are tool-description failures, not reasoning failures. The
model cannot read your code; the schema and the description are the entire
interface, and a model that picks the wrong tool was told the wrong thing.

```python
# Bad — describes the implementation
{"name": "query_db",
 "description": "Runs a parameterized SELECT against the orders table."}

# Good — describes when to call it, what comes back, and what it is not for
{"name": "find_orders",
 "description": (
   "Find a customer's orders. Use when the user references an order by number, "
   "date, or 'my last order'. Returns up to 20 orders, newest first, each with "
   "id, status, total, and placed_at. Does NOT return line items — call "
   "get_order_details for those. Returns an empty list if the customer has no "
   "orders; that is not an error."
 )}
```

Four things every description needs: **when to call it**, **what it returns**,
**what it does not do and which tool does that instead**, and **what an empty or
edge-case result means**. Put units, formats, and enumerated values in the
parameter descriptions, with an example — `"placed_after": "ISO 8601 date, e.g.
2026-03-01. Defaults to 90 days ago."` — because a model guessing at a date
format will guess wrong at exactly the rate you would expect.

### 2. Make Errors Tell the Model What to Do Next
An error is a turn in a conversation. `{"error": "invalid input"}` gives the model
nothing to act on, so it retries identically until the budget runs out.

```python
# Useless
{"error": "400 Bad Request"}

# Actionable
{"error": "invalid_argument",
 "message": "placed_after must be ISO 8601 (YYYY-MM-DD); received 'last Tuesday'",
 "retryable": true,
 "hint": "Resolve relative dates before calling. Today is 2026-09-18."}

# Actionable, and redirects
{"error": "not_found",
 "message": "No customer with email 'jo@example.com'",
 "retryable": false,
 "hint": "Try search_customers with a partial name, or ask the user for the order number."}
```

Return errors as *results*, not exceptions — a crashed tool call the model never
sees is a turn it cannot learn from. Always include whether retrying could help:
`retryable: false` is what stops a model from looping on a permanent failure.

### 3. Bound the Loop on Three Axes
An agent loop without limits ends in a repeating cycle costing real money. Budget
all three, and make the reason for stopping visible:

| Budget | Typical | Failure it prevents |
|---|---|---|
| Steps | 10–25 tool calls per task | Two tools calling each other in a cycle |
| Tokens / cost | A hard ceiling per task | Context growth making each step more expensive than the last |
| Wall clock | 30–120 s | A slow tool stalling a user-facing request |

Also stop on **no progress**: if the last three calls were identical in name and
arguments, the model is stuck and another attempt will not help. Break out and say
so, rather than exhausting the step budget in silence.

When a budget trips, return a partial answer with what was accomplished. Silent
truncation looks to the user like the agent hallucinated an incomplete result.

### 4. Control Cost Where It Actually Accrues
Cost in a multi-step loop is driven by re-sending context, not by the number of
steps. Every step resends the whole transcript, so an early 8,000-token tool result
is paid for on every subsequent step.

- **Cap and paginate tool output.** Return 20 rows with a `next_cursor`, never 500.
  Truncate long text with an explicit marker so the model knows it is partial.
- **Return ids and summaries, let the model fetch detail.** Breadth-then-depth is
  cheaper than dumping everything on the chance it is needed.
- **Prune old tool results** from the transcript once superseded, keeping the
  assistant's reasoning about them.
- **Cache the stable prefix** — system prompt and tool definitions rarely change,
  and providers that support prefix caching make that the cheapest available win.
- **Do not hand the agent 40 tools.** Selection accuracy falls as the surface grows
  and every definition is resent every step. Scope tools to the task.

### 5. Split or Merge Tools by Decision, Not by Endpoint
The right granularity is one tool per decision the model makes.

**Merge** when the model always calls them in the same order and has no real choice
— `get_user_id` followed immediately by `get_user_profile` is one tool. Every extra
hop is a step, a round trip, and a chance to get the arguments wrong.

**Split** when a single tool needs a `mode` or `action` parameter that changes the
meaning of other parameters, when one branch is read-only and another writes, or
when the description needs "if X then also pass Y". `manage_order(action=...)`
forces the model to reason about a parameter matrix; `cancel_order`,
`refund_order`, and `get_order` each have one job and one description.

### 6. Make Every Side-Effecting Tool Idempotent
The model will retry — after a timeout, after an ambiguous error, after it reasons
itself into calling the same tool twice. Without idempotency, that is two refunds.

```python
def issue_refund(order_id: str, amount: Decimal, idempotency_key: str) -> dict:
    if prior := refunds.get(idempotency_key):
        return {**prior, "replayed": True}       # same result, no second charge
    ...
```

Derive the key from the intent (`refund:{order_id}:{amount}`), not from a random
value the model generates — a model asked to invent a unique key on a retry will
invent a *different* one, which defeats the entire mechanism. For genuinely
non-idempotent, high-consequence actions, require a confirmation step: a `preview`
tool returning exactly what will happen, then a `commit` tool taking the token the
preview returned. See `idempotency-patterns`.

## Warning Signs

- Tool descriptions written from the implementation rather than the call site
- No statement of what a tool does *not* do, or which tool to use instead
- Parameter formats, units, and enums undocumented; no example values
- Errors returned as bare strings, HTTP codes, or raised exceptions
- No `retryable` signal, so the model loops on permanent failures
- No step, token, or wall-clock budget on the loop
- No no-progress detection; identical calls repeating until the budget expires
- Budget exhaustion returning nothing instead of a partial result
- Tool results returning hundreds of rows or whole documents unpaginated
- Dozens of tools exposed to a single agent
- A `mode` or `action` parameter that changes what the other parameters mean
- Side-effecting tools with no idempotency key, or a key the model invents freshly
- Irreversible actions with no preview-then-commit step
