# LLM Application Architecture (Verbose)

## Core Patterns

### The Triangle: Latency, Cost, Quality — Two Per Call Site

Every architectural decision in an LLM application is a trade among three
quantities, and the trade is made per call site rather than per application. A
product with a chat surface, a background summarizer, and an inline suggestion
box has three different right answers, and forcing one model and one prompt
across all three is the most common structural mistake.

| Call site | Human waiting? | Volume | Optimize | Accept | Shape |
|---|---|---|---|---|---|
| Inline suggestion | Yes, sub-second | Very high | Latency | Lower quality | Small model, minimal context, streamed, aggressive timeout |
| Interactive chat | Yes, seconds | High | Latency + quality | Cost | Large model, cached prefix, streamed, tools |
| Bulk enrichment | No | Very high | Cost | Latency | Small model, batch endpoint, buffered, retried freely |
| Document analysis | No, minutes ok | Low | Quality | Cost + latency | Large model, long context, multi-pass, self-check |
| Agentic task loop | Loosely | Low | Quality | Latency + cost | Large model, many turns, per-loop token ceiling |

Convert the choice into two numbers before writing a prompt:

```yaml
call_site: support_chat_reply
budget:
  p95_latency_ms: 2500
  p95_time_to_first_token_ms: 600
  cost_per_request_usd: 0.004
  max_input_tokens: 12000
  max_output_tokens: 800
degradation:
  on_timeout: return_cached_greeting_and_handoff
  on_rate_limit: small_model
```

Budgets belong in configuration next to the prompt, and they belong on a
dashboard as a per-request unit cost. The failure this prevents is specific:
without a stated budget, every prompt iteration adds a few hundred tokens of
instructions and a few more few-shot examples, each change individually
reasonable, and three months later the feature costs six times its launch price
with no one able to name the commit that did it.

### Context Window Budgeting

Treat the window as a fixed allocation split across named consumers, with a
reserve. The consumers compete, and the one that grows without bound is always
retrieved documents or conversation history.

| Consumer | Typical share | Growth behavior | Eviction rule |
|---|---|---|---|
| System prompt | Small, fixed | Grows by edit only | Review like code; never truncate |
| Tool definitions | Small–medium | Grows with tool count | Expose only the tools this route can call |
| Retrieved documents | Large | Grows with k | Drop lowest-ranked whole documents |
| Conversation history | Unbounded | Grows every turn | Drop or summarize oldest whole turns |
| Output reserve | Medium | Fixed by max_tokens | Never lend it out |

```python
def assemble_context(system, tools, docs, history, *, window, budget):
    reserve = budget["reserve_for_output"]
    fixed = count_tokens(system) + count_tokens(tools)
    room = window - reserve - fixed
    if room <= 0:
        raise ContextBudgetError("fixed prompt exceeds window; shrink tools or system")

    docs_txt = take_while_under(docs, min(budget["retrieved"], room), unit="document")
    room -= count_tokens(docs_txt)
    hist_txt = take_recent_under(history, min(budget["history"], room), unit="turn")

    ctx = join(system, tools, docs_txt, hist_txt)
    emit_metric("context.tokens", count_tokens(ctx), tags={"site": budget["name"]})
    return ctx
```

Three rules do most of the work:

**Drop whole units, never bytes.** A document cut mid-sentence contributes a
fact fragment the model will happily complete from its own priors. A turn cut in
half leaves an unanswered user question in the history. Both produce confident
wrong answers that look like model failures.

**Always reserve output tokens.** If input plus output exceeds the window, the
generation stops at the boundary with a length stop reason. Teams read the
truncated answer, conclude the model "trails off", and respond by adding
instructions telling it to be complete — which consumes more input tokens and
makes it worse.

**Instrument the token count, not just the cost.** Context size is the leading
indicator; cost and latency are the lagging ones. Alert when p95 context tokens
for a call site exceed 80% of the window, because that is when truncation starts
silently.

For long conversations, rolling summarization beats a sliding window: summarize
the oldest turns into a compact state block, keep the last few turns verbatim.
The verbatim tail matters — models follow recent instructions and recent format
examples far more reliably than summarized ones.

### Streaming vs Buffered

| Dimension | Streaming | Buffered |
|---|---|---|
| Perceived latency | Time-to-first-token, often 10x better | Full generation time |
| Total tokens and cost | Identical | Identical |
| Validate before display | Impossible | Yes |
| Retry invisibly | Only before the first token ships | Always |
| Post-process (redact, reformat, cite) | Hard; needs incremental parsing | Trivial |
| Cancel on user abandon | Yes, stop paying mid-generation | No, you pay for the whole thing |
| Error surface | Mid-stream errors after partial output | One clean error |

The decision rule is who consumes the bytes. Human reading prose: stream. A
parser, a validator, or another service: buffer.

The expensive mistake is streaming structured output to a client that parses it
incrementally. The model emits a JSON object, the client renders fields as they
arrive, and then the object turns out to be malformed or to have hallucinated an
enum value. Now you must retract UI the user has already read. Buffer structured
output, validate it, and stream only prose.

A useful middle path for agentic flows: stream *status*, buffer *content*. The
user sees "searching the knowledge base… reading 4 documents… drafting", which
covers the latency socially, while the answer itself is validated before it
appears.

```python
async def respond(req):
    async for event in agent.run(req):
        if event.kind == "progress":
            yield sse("status", event.label)          # stream
        elif event.kind == "final":
            payload = validate_or_repair(event.text)  # buffer, then validate
            yield sse("answer", payload)
```

Set a time-to-first-token deadline separately from the overall deadline. A
stream that opens in 400ms and finishes in 9s is usually fine; one that opens in
6s is not, even if it finishes sooner overall.

### Model Selection and Routing

Traffic is not uniformly difficult. A cascade sends everything to a small model
and promotes only what fails a check.

```python
def answer(prompt, *, route):
    small = call(route.small_model, prompt)
    if escalate(small):
        return call(route.large_model, prompt), "escalated"
    return small, "small"

def escalate(r) -> bool:
    return (r.stop_reason == "refusal"
            or not schema_valid(r)
            or r.parsed.get("label") == "uncertain"
            or r.parsed.get("needs_tools"))
```

The economics are worth doing explicitly. If the large model costs `C_L`, the
small one `C_S`, and the escalation rate is `e`, the cascade costs
`C_S + e·C_L`. It only pays when `e < (C_L − C_S) / C_L`. With a small model at
a tenth the price, the break-even escalation rate is around 90% — comfortable.
But latency does not divide the same way: an escalated request pays *both*
models serially, so p99 latency gets worse even as mean cost improves. Cascades
belong on cost-sensitive, latency-tolerant call sites, and rarely on the
inline-suggestion path.

| Escalation signal | Trustworthy? | Notes |
|---|---|---|
| Schema validation failed | Yes | Structural, cheap, unambiguous |
| Explicit `uncertain` enum in the output contract | Yes | Give the model a legitimate way to decline |
| Required tool call absent | Yes | The small model did not recognize the task |
| Retrieval scores all below threshold | Yes | The question is out of corpus; escalating may not help either |
| Output length anomaly | Weak | Noisy, but cheap to compute |
| Model's self-reported confidence number | No | Poorly calibrated; correlates with fluency, not correctness |
| A second LLM call asking "was that right?" | Costly | You have now paid for two calls to decide whether to pay for a third |

Route by *task*, not by user tier, wherever you can. "Premium users get the big
model" is easy to build and hard to defend: it makes quality a billing artifact
rather than a property of the task, and it produces support tickets that are
impossible to reproduce.

Keep model ids in configuration, never inlined at call sites, and log the id
with every request. When you change models, that log is the only way to
attribute a quality regression or a cost change to the switch.

### Caching: Two Layers That Solve Different Problems

| | Prompt / prefix cache | Semantic cache | Exact-match cache |
|---|---|---|---|
| Key | Byte-identical token prefix | Embedding similarity | Hash of the full request |
| Hit saves | Re-processing the prefix | The whole call | The whole call |
| Correctness risk | None | Real — a near-miss returns the wrong answer | None |
| Invalidation | Automatic, by prefix change | Hard; needs TTL and scoping | Easy |
| Best for | Long stable system prompts, few-shot blocks, a document reused across turns | High-volume repeated questions over stable content | Deterministic, idempotent calls |

**Prompt caching** is close to free and mostly an ordering discipline: put
everything static first, in a stable byte order, and everything volatile last.

```
[ system prompt ][ tool definitions ][ few-shot block ][ retrieved docs ]  <- cacheable prefix
[ conversation history ][ current user message ][ "current time: ..." ]    <- volatile tail
```

One injected timestamp or a user's name at the top of the system prompt
invalidates the entire prefix on every request. So does a dictionary serialized
in nondeterministic key order, or a retrieval step that returns the same
documents in a different order — sort retrieved documents by a stable id before
assembly, not by score, when they are going into a cached prefix.

**Semantic caching** is where the bugs are. Two requests with 0.95 cosine
similarity can require opposite answers: "did my refund go through" and "how do
I get a refund"; "cancel my subscription" and "don't cancel my subscription".
Guardrails that make it survivable:

- Threshold high (0.95+), and tune it against a labeled set of near-miss pairs,
  not by intuition.
- Scope the key by tenant, user, locale, and prompt version — never a global
  namespace.
- Never cache a response generated from personalized or permissioned context.
  Leaking one tenant's answer to another is a security incident, not a cache
  bug.
- TTL short enough to respect content updates, and invalidate on corpus change.
- Log hits with both questions so you can audit near-misses; sample a share of
  hits to the live model to measure the cache's actual error rate.

### Failure Modes and Graceful Degradation

| Failure | How it presents | Wrong response | Right response |
|---|---|---|---|
| Timeout | No tokens, or stream stalls mid-generation | Retry immediately, same model, same deadline | Overall deadline budget; serve partial output or a cached/templated answer; degrade to the small model |
| Truncation | Stop reason `length` | Raise max_tokens until it fits | Reserve output tokens; shrink input; or design the task to emit in segments |
| Rate limit (429) | Bursty, correlated across your fleet | Tight retry loop | Exponential backoff with jitter, a concurrency limiter, a queue for non-interactive work, and shed to a second provider or smaller model |
| Malformed / unparseable output | Schema validation fails | Loosen the parser | One repair retry with the validation error included, then a deterministic fallback |
| Refusal or safety stop | Empty or policy response | Rephrase and retry blindly | Detect it, log it, route to the non-LLM path or a human |
| Content policy on input | 4xx | Surface a stack trace | Explicit user-facing message; never retry |
| Upstream outage | Sustained 5xx | Let every request hang | Circuit breaker, then the degraded path for the whole feature |

Three patterns carry most of the weight:

**A deadline budget, not a per-call timeout.** A request with 3s of user
patience and three sequential LLM calls cannot give each one 3s. Pass a
remaining-time budget down the stack and let each step decide whether it has
room to run at all.

```python
async def call_with_budget(fn, deadline: float, *a, **kw):
    remaining = deadline - time.monotonic()
    if remaining < MIN_USEFUL_SECONDS:
        raise BudgetExhausted
    return await asyncio.wait_for(fn(*a, **kw), timeout=remaining)
```

**A circuit breaker in front of the provider.** Without one, a provider
slowdown converts into every worker thread parked on a socket, and the outage
spreads to parts of the product that never touch the model. Open the breaker on
sustained errors, serve the degraded path, and probe with a trickle.

**A defined degraded experience per feature.** Write it down alongside the
budget: search falls back to keyword results, the summarizer shows the raw
document, the chat surface offers a handoff. "Spinner until the gateway gives
up" is the default only because nobody chose otherwise.

Retries deserve their own caution: LLM calls are expensive and not idempotent
in cost. A retry storm during a provider degradation multiplies spend exactly
when latency is worst. Cap retries at one or two, jitter them, and make the
retry budget global (a token bucket across the fleet) rather than per request.

### Observability for LLM Call Sites

You cannot manage the triangle without measuring all three corners per call
site, per model version, per prompt version.

```python
log_llm_call({
    "call_site": "support_chat_reply",
    "request_id": req.id,
    "model": route.model_id,           # from config, never inlined
    "prompt_version": PROMPT_VERSION,  # see the prompt-engineering skill
    "input_tokens": usage.input, "cached_input_tokens": usage.cached,
    "output_tokens": usage.output,
    "cost_usd": cost(usage, route),
    "ttft_ms": ttft, "total_ms": total,
    "stop_reason": resp.stop_reason,   # length / stop / tool_use / refusal
    "escalated": escalated, "cache": "prefix_hit",
    "validation": "ok",
})
```

The fields that repeatedly earn their place: `stop_reason`, which distinguishes
truncation from a genuine finish and is the single highest-signal field on the
list; `cached_input_tokens`, which tells you whether the prefix cache is
actually working rather than being invalidated every request; `prompt_version`,
which makes quality regressions attributable; and `escalated`, which is the
cascade's economics in one boolean.

## Common Anti-Patterns

❌ **One model and one prompt for every call site.**
✅ Budget each site on latency, cost, and quality separately, and route accordingly.

❌ **Assembling context by string concatenation with no token accounting.**
✅ A named budget per consumer, whole-unit eviction, and a reserved output allocation.

❌ **Truncating documents or turns mid-content to fit.**
✅ Drop whole documents or whole turns, lowest value first; summarize the old history.

❌ **Streaming structured output and parsing it incrementally.**
✅ Buffer and validate anything a program consumes; stream prose and status only.

❌ **Escalating on the model's self-reported confidence.**
✅ Escalate on structural signals: failed validation, an explicit `uncertain` value, a missing tool call.

❌ **A timestamp or user name at the top of the system prompt.**
✅ Static first in a byte-stable order, volatile last, so the prefix cache actually hits.

❌ **A globally keyed semantic cache with a permissive threshold.**
✅ High threshold, scoped by tenant and user, short TTL, never over personalized context, with hit auditing.

❌ **Per-call timeouts with no overall deadline, and unbounded retries.**
✅ A deadline budget passed down the call chain, jittered retries, a fleet-wide retry budget, and a circuit breaker.

❌ **No defined answer to "what does the user see when the model does not return?"**
✅ A written degraded path per feature: cached answer, keyword fallback, raw document, human handoff.

❌ **Cost reviewed monthly in aggregate.**
✅ Cost per request per call site on a dashboard, with an alert on the unit cost, not the total.

## LLM Architecture Checklist

- [ ] Every call site has a written latency, cost, and token budget in config
- [ ] Context assembled through a budgeted assembler with a reserved output allocation
- [ ] Eviction drops whole documents and whole turns, never partial content
- [ ] Context token count instrumented, with an alert near the window limit
- [ ] Streaming chosen by consumer: prose to humans, buffered and validated for programs
- [ ] Separate time-to-first-token and total-latency objectives
- [ ] Model ids in configuration and logged per request, never inlined
- [ ] Cascade routing where it pays, with the escalation rate measured against break-even
- [ ] Escalation driven by structural signals, not self-reported confidence
- [ ] Prompt prefix ordered static-first with a stable byte serialization; cached-token share monitored
- [ ] Semantic cache, if used, scoped per tenant, thresholded, TTL'd, and audited for near-miss hits
- [ ] Deadline budget threaded through multi-call flows
- [ ] Jittered, capped retries with a fleet-wide retry budget and a circuit breaker
- [ ] A documented degraded experience per feature for timeout, rate limit, and outage
- [ ] `stop_reason`, token usage, cost, and prompt version logged on every call
