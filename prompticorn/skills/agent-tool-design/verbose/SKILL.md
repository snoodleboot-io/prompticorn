# Agent Tool Design (Verbose)

## Core Patterns

### The Description Is the Interface

Most agent failures are tool-description failures, not reasoning failures. When an
agent calls the wrong tool, passes a malformed date, or loops on an error, the
first place to look is not the prompt or the model — it is the schema. The model
cannot read your implementation, your tests, or your intentions. It sees a name, a
description, a parameter schema, and whatever came back last time.

This reframes debugging usefully. "The model is not smart enough to know that
`find_orders` needs the customer id, not the email" is a description that omitted
which identifier the parameter takes.

A description has four jobs:

| Job | Question it answers | Consequence of omitting it |
|---|---|---|
| Trigger | When should this be called? | Tool never called, or called for the wrong situation |
| Return contract | What comes back, in what shape, how much? | Model plans around imagined output |
| Boundary | What does it *not* do, and what does that instead? | Wrong tool chosen between similar options |
| Edge semantics | What does empty / zero / null mean here? | Empty result read as an error, or vice versa |

```python
{
  "name": "find_orders",
  "description": (
    "Find a customer's orders, newest first. Use this when the user refers to an "
    "order by number, by date, or loosely ('my last order', 'the one from March').\n"
    "Returns up to 20 orders; each has id, status, total_usd, placed_at, and "
    "item_count. Use the returned cursor for more.\n"
    "Does NOT return line items, shipping events, or refunds — call "
    "get_order_details(order_id) for those.\n"
    "An empty list means this customer has no orders in the range. That is a "
    "normal result, not an error."
  ),
  "input_schema": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "Internal customer id, e.g. 'cus_8812'. NOT an email "
                       "address — resolve emails with find_customer first."
      },
      "status": {
        "type": "string",
        "enum": ["pending", "shipped", "delivered", "cancelled"],
        "description": "Optional. Omit to return all statuses."
      },
      "placed_after": {
        "type": "string",
        "description": "Optional ISO 8601 date, e.g. '2026-03-01'. Resolve "
                       "relative dates ('last month') before calling. "
                       "Defaults to 90 days ago."
      },
      "cursor": {"type": "string", "description": "From a previous response's next_cursor."}
    },
    "required": ["customer_id"]
  }
}
```

Specific habits that pay for themselves:

- **Name for intent, not implementation.** `find_orders` over `query_orders_table`.
  The name is the strongest signal in tool selection and is often all a model reads
  before deciding two tools are different.
- **Disambiguate similar tools inside both descriptions.** If `search_docs` and
  `get_doc` coexist, each should say when the other is correct. Selection errors
  cluster on near-neighbours, and the fix is mutual cross-referencing.
- **Enumerate rather than describe.** `enum: [...]` is enforced; "one of the valid
  statuses" is not.
- **Give one example value per non-obvious parameter.** Date formats, id prefixes,
  and unit conventions are guessed wrongly with high reliability.
- **State units in the name when ambiguity is possible.** `total_usd`,
  `timeout_ms`, `size_bytes`. A bare `amount` will be passed in the wrong scale
  eventually.
- **Say what is expensive or irreversible.** "This sends an email to the customer
  immediately" changes how cautiously a model uses it, and costs nothing to add.

**Evaluate descriptions the way you evaluate prompts.** Build a set of realistic
requests, record which tool the model selects and with what arguments, and assert
on both. Tool-selection accuracy is a deterministic, reference-based metric — the
easiest thing in the whole LLM stack to test properly (see
`llm-evaluation-and-testing`). When accuracy is poor, rewrite the description and
re-measure; do not reach for a bigger model first.

### Error Surfaces That Enable Recovery

A tool error is a message in a conversation with a model that can act on it. Most
implementations waste it entirely, returning either a raised exception the model
never sees or a string with no actionable content, after which the model retries
the identical call until a budget stops it.

| Error style | Model's likely next move |
|---|---|
| Exception propagates, loop crashes | Nothing — the user gets a 500 |
| `"error": "Internal server error"` | Retry identically, repeatedly |
| `"error": "400 Bad Request"` | Retry with a randomly different argument |
| Typed error + message + retryable + hint | Fix the argument, or switch tools, or ask the user |

A response shape worth standardising across every tool:

```python
@dataclass
class ToolError:
    error: str          # stable machine code: invalid_argument, not_found, ...
    message: str        # what specifically was wrong, quoting the bad value
    retryable: bool     # would an identical retry ever succeed?
    hint: str | None    # concrete next action for the model
    fields: dict | None # per-parameter detail for validation failures
```

Concretely, by class:

```python
# Validation — tell it the rule and the received value
ToolError("invalid_argument",
          "placed_after must be ISO 8601 (YYYY-MM-DD); received 'last Tuesday'",
          retryable=True,
          hint="Today is 2026-09-18; resolve relative dates before calling.",
          fields={"placed_after": "expected YYYY-MM-DD"})

# Not found — redirect rather than dead-end
ToolError("not_found",
          "No customer with id 'jo@example.com'",
          retryable=False,
          hint="That looks like an email. Call find_customer(email=...) to get "
               "the customer id, then retry.")

# Permission — stop the loop; no retry will help
ToolError("forbidden",
          "This API key cannot issue refunds above $500.00",
          retryable=False,
          hint="Call escalate_to_human with the order id and reason.")

# Transient — retry is genuinely correct
ToolError("unavailable",
          "Orders service timed out after 5s",
          retryable=True,
          hint="Retry once. If it fails again, tell the user the system is "
               "temporarily unavailable rather than guessing at order data.")

# Too large — the recovery is a narrower query
ToolError("result_too_large",
          "Query matched 14,203 orders; the limit is 200",
          retryable=True,
          hint="Add a status filter or narrow placed_after, then retry.")
```

Three rules underneath these:

1. **Errors are results, not exceptions.** Catch everything at the tool boundary
   and return it as content the model can read. An unhandled exception removes the
   agent's only chance to recover.
2. **`retryable` is the field that prevents loops.** Combine it with a per-tool
   retry cap: on a second identical failure, escalate or surface to the user rather
   than letting the model discover futility by exhausting the budget.
3. **Never leak internals.** Stack traces, SQL, and internal hostnames burn context,
   teach nothing, and may reach the user through the model's summary.

And a subtler one: **validate strictly and reject clearly rather than guessing.**
Coercing `"last Tuesday"` into a date the model did not intend produces a wrong
answer delivered confidently. A clear rejection produces a corrected call. Silent
coercion is the worse failure because nothing in the transcript records it.

### Loop Termination and Step Budgets

An agent loop is `while True` around a model call. Without explicit termination it
will, eventually and in production, cycle: tool A suggests tool B, tool B's result
prompts tool A, and the loop runs until something external stops it.

Budget on four axes, because each catches a different pathology:

| Axis | Sensible start | Catches |
|---|---|---|
| Step count | 10–25 calls per task | Cycles between tools; aimless exploration |
| Cumulative tokens / cost | A hard per-task ceiling | Context growth making late steps far pricier than early ones |
| Wall clock | 30–120 s, tighter for interactive | A slow dependency stalling a user-facing request |
| No-progress | 2–3 identical calls | The model stuck repeating itself, which more steps will not fix |

```python
def run(task, tools, max_steps=20, max_cost_usd=0.50, deadline_s=90):
    started, spent, recent = time.monotonic(), 0.0, deque(maxlen=3)
    for step in range(max_steps):
        if spent >= max_cost_usd:
            return partial(msgs, "cost budget exhausted")
        if time.monotonic() - started > deadline_s:
            return partial(msgs, "time budget exhausted")

        resp = model(msgs, tools); spent += resp.cost
        if not resp.tool_calls:
            return done(resp.text)                     # normal termination

        for call in resp.tool_calls:
            sig = (call.name, canonical(call.args))
            if len(recent) == recent.maxlen and all(s == sig for s in recent):
                return partial(msgs, f"no progress: {call.name} repeated")
            recent.append(sig)
            msgs.append(execute(call))                 # errors included, as results
    return partial(msgs, "step budget exhausted")
```

Points that matter more than the numbers:

- **Every exit returns a partial result, never nothing.** `partial()` asks the model
  to summarise what it established and what remains unknown. A truncated loop that
  returns silence is indistinguishable, from the user's side, from a fabricated
  incomplete answer.
- **No-progress detection is the highest-value limit.** A model repeating an
  identical call three times has no new information and will not acquire any. This
  catches in three steps what a step budget catches in twenty, at a twentieth of
  the cost.
- **Canonicalise arguments before comparing.** Key order and whitespace differ
  between otherwise identical calls, and naive comparison misses the repeat.
- **Budgets are per task, not per request.** A long-running agent needs the ceiling
  carried across resumptions, or it is not a ceiling.
- **Emit a metric on every termination reason.** The distribution of
  normal / step / cost / time / no-progress exits is the single most informative
  dashboard an agent system has. A rising no-progress rate is usually a tool
  description or an error surface that stopped working, not a model regression.
- **Give the model an explicit way to give up.** A `report_failure(reason)` or
  `escalate_to_human(summary)` tool lets it terminate cleanly when it cannot
  proceed, rather than flailing until a budget trips. Models use these readily when
  told they exist.

### Cost Control in Multi-Step Loops

The cost model surprises people: in a loop, the *transcript* is resent at every
step, so one large tool result early is paid for by every step after it. A 10-step
task with an 8,000-token result at step two pays that 8,000 roughly eight more
times. Step count grows cost linearly; result size grows it quadratically.

| Lever | Effect | Cost |
|---|---|---|
| Cap and paginate tool results | Removes the quadratic term | An extra step when more is genuinely needed |
| Ids and summaries first, detail on request | Model fetches only what it uses | One more round trip on the paths that need detail |
| Prune superseded tool results | Bounds transcript growth | Care required not to remove what is still referenced |
| Cache the stable prefix | System prompt and tool defs stop being re-billed | Requires provider support; keep the prefix genuinely stable |
| Smaller model for routine steps | Large per-step saving | A routing decision, and two models to evaluate |
| Fewer tools in scope | Smaller definitions resent each step; better selection | Task-scoped tool sets to maintain |

```python
MAX_ROWS, MAX_CHARS = 20, 4000

def find_orders(customer_id, cursor=None, **filters):
    rows, next_cursor = repo.page(customer_id, cursor, limit=MAX_ROWS, **filters)
    return {
        "orders": [
            {"id": r.id, "status": r.status, "total_usd": str(r.total),
             "placed_at": r.placed_at.date().isoformat(), "item_count": r.n_items}
            for r in rows                       # NOT the full row; no internal fields
        ],
        "returned": len(rows),
        "next_cursor": next_cursor,
        "note": None if next_cursor is None else
                "More results exist. Narrow the filters or pass next_cursor.",
    }
```

Two design points hide in that snippet. The projection is deliberate — returning
the ORM row because it is available adds internal fields that consume context and
occasionally leak. And `note` tells the model that truncation happened; silent
truncation causes a model to conclude the customer has exactly 20 orders and answer
accordingly.

**Tool count deserves its own attention.** Selection accuracy degrades as the
surface grows, and every definition is resent every step, so a large tool set is
simultaneously the accuracy problem and the cost problem. Above roughly 15–20
tools, scope them: expose only the tools relevant to the detected task, or split
the work across sub-agents each holding a small, coherent set. A retrieval sub-agent
with four tools and a fresh context is usually both cheaper and more accurate than
one agent with thirty.

**Instrument per task, not per call.** Track steps, total tokens in and out, cost,
wall clock, and termination reason, tagged by task type. Nearly every agent cost
problem turns out to be one task type with a pathological step distribution, and
you cannot see that in an aggregate.

### Granularity: When to Split, When to Merge

The right unit is **one tool per decision the model actually makes**. Not one per
REST endpoint, and not one per domain object.

**Merge when the model has no real choice.** If `get_user_id(email)` is always
followed immediately by `get_user_profile(id)`, that sequence is not a decision —
it is a mechanism, and exposing it costs a step, a round trip, and an opportunity
to pass the wrong id. Collapse it into `get_user(email_or_id)`.

| Merge when | Split when |
|---|---|
| Call B always follows call A with A's output | The model genuinely chooses between the branches |
| The intermediate value has no meaning to the model | One branch is read-only and another has side effects |
| Two tools differ only by a filter that could be a parameter | A `mode`/`action` parameter changes what other parameters mean |
| The sequence is fixed and the model never varies it | The description needs "if X, also pass Y; if Z, that field is ignored" |
| Each step is a round trip on the critical path | The tool returns wildly different shapes per branch |

The `action` parameter is the most common smell:

```python
# Hard for a model: parameter validity depends on `action`
manage_order(action="cancel"|"refund"|"reship"|"get",
             order_id=..., amount=None, reason=None, address=None)

# Each has one job, one description, one schema
get_order(order_id)
cancel_order(order_id, reason)
refund_order(order_id, amount_usd, idempotency_key)
reship_order(order_id, address)
```

The merged version forces the model to reason about a parameter matrix and makes
its description a set of conditionals. It also makes permissions impossible to
express cleanly — `get` is read-only and `refund` moves money, and they now share
one tool with one authorization decision.

The counter-pressure is the tool-count budget above. Resolve it by splitting on
*decision boundaries* and merging on *mechanism*: four order tools that a model
chooses between are fine; four tools that are always called in sequence are one
tool wearing four hats.

One more distinction worth keeping: separate **read** tools from **write** tools
even when they touch the same resource. It lets you grant a read-only agent a
strictly safe surface, makes side effects auditable, and gives the model a clear
signal about which calls are consequential.

### Idempotency and Side Effects

Agents retry. After a timeout whose result is unknown, after an ambiguous error,
after reasoning that reaches the same conclusion twice, and after a loop resumes
from a checkpoint. Without idempotency, each of those is a duplicated side effect —
two refunds, two emails, two tickets.

```python
def issue_refund(order_id: str, amount_usd: Decimal, idempotency_key: str) -> dict:
    if prior := refund_log.get(idempotency_key):
        return {**prior, "replayed": True}     # identical result, no second charge

    with db.transaction():
        if refund_log.get(idempotency_key):    # re-check under lock
            return {**refund_log.get(idempotency_key), "replayed": True}
        result = payments.refund(order_id, amount_usd, ref=idempotency_key)
        refund_log.put(idempotency_key, result)
    return result
```

**Where the key comes from is the part that is usually wrong.** Asking the model to
generate a unique key defeats the mechanism: on a retry the model generates a
*different* unique key, and the duplicate goes through. Derive it from intent
instead:

| Source | Behaviour on retry | Verdict |
|---|---|---|
| Model-generated random value | Different key, duplicate executes | Broken |
| Hash of tool name + canonical arguments | Same key, replayed | Good default |
| Hash including the task/session id | Same key within a task; a genuine second request in a new task works | Best |
| Provider's tool-call id | Same for a literal retry of the same call | Good, but misses semantic repeats |

```python
def derive_key(task_id: str, name: str, args: dict) -> str:
    payload = json.dumps({"t": task_id, "n": name, "a": args}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]
```

Do this in the executor rather than in each tool, so no tool author can forget it.
See `idempotency-patterns` for the general treatment.

**For high-consequence actions, add a confirmation boundary.** Some operations
should not be single-call regardless of idempotency — large refunds, deletions,
outbound communication, anything a user would want to see before it happens:

```python
preview_refund(order_id, amount_usd)
#   -> {"will_refund_usd": "42.00", "to": "card ending 4471",
#       "eta_days": 5, "confirmation_token": "prv_9f3a", "expires_in_s": 300}

commit_refund(confirmation_token="prv_9f3a")
```

The token makes the second call meaningless without the first, gives the
application a natural place to insert human approval, and produces an audit record
of exactly what was proposed against what was executed. Short expiry keeps a stale
token from committing something the context has moved past.

Round it out with the boring controls: **scope credentials per tool** so a search
tool cannot write; **rate-limit per task** as well as per key, since one agent in a
loop can exhaust a shared quota; **log every call with its arguments, result
summary, task id, and idempotency key**, which is both the audit trail and the raw
material for every eval set you will build later; and **define what rollback means**
for each side effect before shipping it, because an agent that half-completes a
multi-step action is the normal case, not the exception.

## Common Anti-Patterns

❌ **Descriptions written from the implementation.** "Runs a parameterized SELECT"
tells the model nothing about when to call it.
✅ Trigger, return contract, boundary, and edge semantics, in that order.

❌ **No statement of what a tool does not do.** Selection errors cluster between
near-identical tools with nothing distinguishing them.
✅ Each description names the sibling tool and when to prefer it.

❌ **Undocumented formats, units, and enums.** A model guessing a date format or a
currency scale guesses wrong at a predictable rate.
✅ Enums enforced in the schema; one example per non-obvious parameter; units in
the field name.

❌ **Blaming the model for tool-selection errors.** The bigger model masks a
description problem that is still there.
✅ Measure selection accuracy on realistic requests; rewrite the description; re-measure.

❌ **Exceptions escaping the tool boundary.** The loop dies, the model never sees
the failure, the user gets a 500.
✅ Catch at the boundary; return errors as readable results.

❌ **Opaque errors — bare status codes or "internal error".** The model retries
identically until a budget stops it.
✅ Typed code, the offending value quoted, `retryable`, and a concrete hint.

❌ **No `retryable` signal.** Permanent failures are retried until exhaustion.
✅ State it explicitly, with a per-tool retry cap and an escalation path.

❌ **Coercing malformed arguments silently.** A guessed value produces a confidently
wrong answer with nothing in the transcript recording the guess.
✅ Reject clearly and say what the correct form is.

❌ **Leaking stack traces, SQL, or hostnames into tool results.** Context burned, no
recovery value, possible disclosure through the model's summary.
✅ A clean message; the detail goes to logs.

❌ **A loop with no step, cost, or time budget.** It ends when someone notices the bill.
✅ All four axes, including no-progress detection.

❌ **No no-progress detection.** Identical calls repeat until the step budget expires,
paying twenty times for a conclusion available after three.
✅ Compare canonicalised call signatures; break on repetition.

❌ **Budget exhaustion returning nothing.** Indistinguishable from a fabricated
partial answer.
✅ Always return what was established, what is unknown, and why it stopped.

❌ **No escape hatch for the model.** Unable to give up cleanly, it flails.
✅ A `report_failure` or `escalate_to_human` tool, and a description saying when to use it.

❌ **Unbounded tool results.** Five hundred rows at step two are re-billed at every
later step.
✅ Cap, project, paginate, and say when output was truncated.

❌ **Silent truncation.** The model reports 20 orders as if that were all of them.
✅ Return `next_cursor` and an explicit note.

❌ **Thirty tools on one agent.** Selection accuracy falls and every definition is
resent each step.
✅ Task-scoped tool sets, or sub-agents with small coherent surfaces.

❌ **An `action` or `mode` parameter that changes what other parameters mean.**
✅ One tool per decision, each with its own schema and permission boundary.

❌ **Splitting a fixed sequence into separate tools.** Two calls the model never
varies are one tool, two round trips, and one extra chance to pass a wrong id.
✅ Merge mechanism; split decisions.

❌ **Read and write operations sharing a tool.** No way to grant a safe read-only
surface, and side effects are harder to audit.
✅ Separate them even on the same resource.

❌ **Side-effecting tools with no idempotency key.** A retry after a timeout issues
the refund twice.
✅ Key derived from task id plus canonical arguments, enforced in the executor.

❌ **Asking the model to generate the idempotency key.** On retry it generates a
different one and the duplicate executes.
✅ Derive it deterministically from intent.

❌ **Irreversible high-consequence actions as a single call.** Nowhere to put human
approval and no record of what was proposed.
✅ Preview returning a short-lived confirmation token, then commit against it.

❌ **One credential shared by every tool.** A search tool holds write scope it never needs.
✅ Per-tool scoping, and rate limits per task as well as per key.

## Agent Tool Design Checklist

- [ ] Every tool named for intent, not implementation
- [ ] Every description states trigger, return contract, boundary, and edge semantics
- [ ] Similar tools cross-reference each other and say when to prefer which
- [ ] Parameters carry units, formats, enums, defaults, and one example each
- [ ] Expensive or irreversible tools say so in the description
- [ ] Tool-selection accuracy measured on realistic requests and tracked over time
- [ ] All exceptions caught at the tool boundary and returned as results
- [ ] Errors carry a stable code, the offending value, `retryable`, and a hint
- [ ] Non-retryable errors named clearly so the loop stops instead of retrying
- [ ] Malformed arguments rejected with the correct form, never coerced silently
- [ ] Internal detail (traces, SQL, hostnames) kept out of tool results
- [ ] Step, cost, and wall-clock budgets enforced per task, carried across resumptions
- [ ] No-progress detection on canonicalised call signatures
- [ ] Every termination path returns a partial result and a stated reason
- [ ] Termination reasons emitted as a metric and dashboarded
- [ ] An explicit failure or escalation tool available to the model
- [ ] Tool results capped, projected to needed fields, and paginated with a cursor
- [ ] Truncation signalled explicitly in the result
- [ ] Tool count per agent bounded; sets scoped by task or split across sub-agents
- [ ] Stable prompt prefix cached where the provider supports it
- [ ] Granularity reviewed: mechanism merged, decisions split
- [ ] Read tools separated from write tools, with distinct credentials
- [ ] Idempotency keys derived from task id plus canonical arguments in the executor
- [ ] High-consequence actions behind preview-then-commit with a short-lived token
- [ ] Per-task rate limits in addition to per-key limits
- [ ] Every call logged with arguments, result summary, task id, and idempotency key
- [ ] Rollback semantics defined for each side effect before it ships
