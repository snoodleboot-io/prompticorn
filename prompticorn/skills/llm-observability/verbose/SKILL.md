# LLM Observability (Verbose)

## Core Patterns

### The Dependency You Cannot Version-Pin

The model is a dependency you do not control and cannot version-pin by default,
so your telemetry is the only way you learn it changed.

Every other dependency announces itself. A library upgrade is a diff in a
lockfile; a breaking API change returns a 400; a database migration has a
timestamp. A model can change behaviour with nothing on your side moving at all:
a floating alias rolls onto a newer snapshot, a provider adjusts serving or
quantisation, a safety policy tightens, a dated snapshot reaches end-of-life and
requests are migrated. Your build stays green, your error rate stays flat, and
your outputs are different.

This produces the characteristic failure: quality regressions are blamed on
whatever *did* change on your side. Two weeks of prompt archaeology, a rollback
that does not help, and eventually someone notices the drop lines up with a date
nobody on the team owns.

The countermeasure is one field, recorded on every single call:

```python
span.set_attributes({
    "llm.model.requested":  cfg.model,          # the alias or id you asked for
    "llm.model.resolved":   resp.model,         # the id the provider says it ran
    "llm.model.fingerprint": getattr(resp, "system_fingerprint", None),
    "llm.prompt.version":   PROMPT_VERSION,     # your prompt's git-tracked id
    "llm.params.hash":      hash_params(cfg.params),
    "llm.provider":         cfg.provider,
    "llm.provider.region":  cfg.region,
})
```

Then one alert: for a fixed `llm.model.requested`, the set of distinct
`llm.model.resolved` values changed in the last hour. It fires rarely and it is
the highest-value alert in an LLM stack, because it converts an unattributable
quality mystery into a dated event with a cause.

Two habits go with it. Pin to explicit dated snapshots rather than floating
aliases wherever the provider offers them, so upgrades become a deliberate PR
gated by your eval suite. And treat the deprecation calendar as an operational
date, not a reading task — the migration will happen with or without you, and
the only question is whether you chose the day.

### Trace the User Action, Not the API Call

A single user action in a modern LLM feature fans out: embed the query, retrieve,
rerank, plan, call two tools, generate, validate, maybe retry, maybe judge. A log
line per model call leaves you unable to answer which stage was slow, which was
expensive, or which one produced the wrong answer.

```
trace 7f2a9c  chat.request  user=u_913  tenant=acme  feature=support_copilot
                            total=4.84s  cost=$0.0312  outcome=answered
 ├─ embed.query                                        model=embed-small    42ms
 ├─ retrieve                k=20 → rerank → 6  scores=[.81 .79 .77 .52 .51 .48]
 │                                                                         180ms
 ├─ llm.generate step=plan  in=2,140  out=96   cache_read=1,900            640ms
 │                          ttft=310ms  tps=61
 ├─ tool.lookup_order       args_hash=9ab1  status=ok  rows=1               90ms
 ├─ llm.generate step=answer in=4,820 out=412 cache_read=1,900           3,700ms
 │                          ttft=880ms  tps=111                      ← 77% of total
 ├─ guardrail.output        checks=6  verdict=pass                          25ms
 └─ feedback                thumbs=null  regenerated=false
```

Conventions that make this usable rather than decorative:

**One trace id, surfaced to the user.** Return it as a response id and show it in
the UI (or in a support tool). When someone reports a bad answer, the id must
retrieve the whole tree: resolved prompts, retrieved chunk ids and scores, tool
arguments, the raw completion, and which guardrails ran. Reproducing a complaint
from a screenshot is how teams lose days.

**Semantic conventions, adopted not invented.** OpenTelemetry's GenAI attribute
names (`gen_ai.request.model`, `gen_ai.usage.input_tokens`,
`gen_ai.operation.name`, and so on) are worth using even where they feel verbose,
because every tracing backend and LLM-observability vendor already understands
them. A bespoke attribute schema locks your history into the first tool you tried.

**Retries as children, not replacements.** A retried call is a second span with
`retry=1` and the failure reason on the first, not an overwrite. Otherwise a
feature that silently retries a third of the time shows a beautiful success rate
and double the cost, and nobody can see why.

**Agent loops get an iteration counter and a hard cap.** `agent.iteration=7` on
each span, with a ceiling enforced in code. Unbounded loops are the single most
expensive LLM production bug, and without the counter they appear on the trace as
"one slow request."

### Token and Cost Accounting

Cost is a first-class product metric here, not a finance concern, because it
changes the design: it decides context budgets, model routing, caching, and
whether a feature can be offered on the free tier at all. A monthly invoice
cannot inform any of those, because it is one number with no dimensions.

Compute it yourself, per call, from the usage the response returns:

```python
RATES = load_rate_table()      # config, with effective_date; never hard-coded inline

def record_usage(span, usage, model, ctx):
    r = RATES[model]
    cost = (usage.input_tokens       * r.input
          + usage.cache_write_tokens * r.cache_write
          + usage.cache_read_tokens  * r.cache_read
          + usage.output_tokens      * r.output) / 1_000_000
    span.set_attributes({
        "gen_ai.usage.input_tokens":  usage.input_tokens,
        "gen_ai.usage.output_tokens": usage.output_tokens,
        "llm.usage.cache_read_tokens": usage.cache_read_tokens,
        "llm.cost_usd": cost,
    })
    emit_metric("llm.cost_usd", cost, tags={
        "feature": ctx.feature, "step": ctx.step, "model": model,
        "tenant": ctx.tenant, "plan": ctx.plan, "env": ctx.env,
    })
    return cost
```

| Dimension | Question it answers | Why you will need it |
|---|---|---|
| feature | Which feature is the spend? | Prioritising optimisation work |
| step | Which stage inside the feature? | Usually one step is 80% of it |
| model | What does routing actually save? | Validating a cheap-first router |
| tenant / plan | Who is unprofitable? | Pricing and abuse detection |
| cache_read share | Is prompt caching working? | A collapse here doubles cost overnight |

**Watch the distribution, not the mean.** LLM cost per request is heavy-tailed:
most requests are ordinary, and a few involve a pasted 200-page document or an
agent that looped eleven times. The mean hides both. Track p50, p95, p99 and max
cost per request, and alert on p99 and on cost per tenant per day. A runaway loop
is visible within minutes on p99 and within a month on the invoice.

**Two derived metrics earn their place.** Cost per successful outcome — resolved
ticket, accepted suggestion, completed extraction — because cost per request
improves when quality gets worse and users retry. And the cache-read share of
input tokens, because prompt caching is usually the largest single lever, and it
breaks silently whenever someone inserts a timestamp or a per-user string near
the front of a prompt.

### Latency: Two Numbers That Move for Different Reasons

| Metric | Composed of | Moves because | Matters for |
|---|---|---|---|
| Time to first token | Queueing + prompt processing + everything you did before the call | Longer prompts, cache misses, slow retrieval, provider load | Streamed human-facing UI |
| Total duration | TTFT + output_tokens ÷ generation rate | Longer outputs, more reasoning, retries | Programmatic consumers, timeouts, agent steps |
| Output tokens/sec | Provider-side generation throughput | Provider capacity, model size | Distinguishing their problem from yours |
| Queue / rate-limit wait | Your client-side backoff | Concurrency limits, bursty traffic | Capacity planning |

Reporting one p95 for total duration merges causes with opposite remedies. TTFT
up with flat throughput means the prompt grew, the cache stopped hitting, or
retrieval is slow — shorten and cache. Total up with flat TTFT means you are
generating more tokens — cap `max_tokens`, tighten the output contract, or stop
asking for a preamble.

```python
t0 = perf_counter(); ttft = None
with client.stream(**req) as stream:
    for chunk in stream:
        if ttft is None and chunk.has_text:
            ttft = perf_counter() - t0
            span.set_attribute("llm.latency.ttft_ms", ttft * 1000)
        yield chunk
total = perf_counter() - t0
span.set_attributes({
    "llm.latency.total_ms": total * 1000,
    "llm.latency.tps": out_tokens / max(total - (ttft or 0), 1e-6),
})
```

Measure from your own edge. Provider-reported latency excludes your retrieval,
your retries, your guardrails, and your serialisation — which is where a
surprising share of wall-clock time lives. And in agent loops, chart latency per
*step* as well as per request: a 12-step agent with a well-behaved 700ms per step
is an eight-second wait, and no single span looks pathological.

### Capturing Payloads Without Creating a Privacy Liability

Metrics tell you something changed. Only the prompts and completions tell you
what, and only they can become an eval set later. A team that logs aggregates
only will, six months in, be writing golden test cases from imagination — which
is exactly how eval sets end up measuring the cases you already handle.

So capture, deliberately:

| Field | Keep | Note |
|---|---|---|
| Resolved system + user prompt | Yes | After templating — the actual tokens sent |
| Retrieved chunk ids and scores | Yes | Ids, not full text, if the corpus is stable |
| Tool calls and arguments | Yes | Redact argument values that carry PII |
| Raw completion | Yes | Pre-guardrail, pre-parse |
| Guardrail verdicts | Yes | Cheap and diagnostic |
| Implicit feedback | Yes | Regenerate, edit, copy, abandon, escalate |
| Explicit feedback | Yes | Thumbs, ratings, free-text |

And constrain it with four controls:

**Redact at emit, in-process.** Scrub secrets and PII classes the task does not
need before the payload leaves the application, never in the sink. A redaction
step downstream means the raw data already crossed a boundary and is in someone's
log index. Pseudonymise consistently (`CUSTOMER_1`, `ACCT_2`) so the trace stays
readable and the case stays usable as an eval example.

**Tier retention by value density.** Metrics 13 months (you want year-over-year);
traces without payloads 30 days; full payloads 7–14 days; curated eval cases
indefinitely, under explicit consent and a documented lawful basis. Most teams
either keep everything forever or nothing at all; neither is defensible.

**Sample by hash bucket, never randomly.** `hash(trace_id) % 100 < 5` keeps a
request whole. Per-span random sampling produces trees with holes, which are
worse than no trace because they mislead. Override sampling to 100% for errors,
refusals, guardrail blocks, thumbs-down, retries, and top-decile cost or latency
— the tail is where every interesting case lives.

**Treat the payload store as production data.** Access-controlled, audited,
region-resident if your data is. It contains, by construction, the most sensitive
free text in your system.

Finally, check the provider side of the ledger: whether prompts are retained,
for how long, whether they train on them, and which subprocessors see them. Your
observability posture includes data you did not choose to store.

### Quality Drift Without Ground Truth

Production LLM traffic has no labels. There is no `y_true` to compare against,
the same input may have several good answers, and quality is often a judgement a
user makes silently. So you approximate from two directions.

**Direction one — a panel of proxies on live traffic.** No single one is quality,
but they rarely all stay flat when quality moves.

| Signal | Cost | Reads on | Lag |
|---|---|---|---|
| Schema / parse failure rate | Free | Format compliance | Seconds |
| Guardrail block + refusal rate | Free | Over-refusal, policy shift | Seconds |
| Retry and fallback rate | Free | Instability, rate limits | Seconds |
| Tool-call error rate, unknown-tool rate | Free | Reasoning quality in agents | Seconds |
| Output length distribution | Free | Verbosity shifts — an early model-change tell | Minutes |
| Regenerate / edit rate | Free | User dissatisfaction | Minutes |
| Abandonment, escalation to human | Free | Task failure | Hours |
| Thumbs-down rate | Free | Explicit, but sparse and biased | Hours |
| LLM-judge score on a traffic sample | $ | Closest to real quality | Minutes |

Output length deserves a mention of its own: a provider-side change very often
shows up first as the median completion getting 15% longer or shorter, days
before anyone files a complaint.

**Direction two — a frozen probe set, run on a schedule.** This is the definitive
half. Take 50–200 representative prompts with reviewed reference outputs, and run
them hourly or nightly against the production configuration.

```python
def run_probe_suite(cfg) -> dict:
    rows = []
    for case in load_probes():                     # frozen, version-controlled
        out = call_model(case.prompt, cfg)
        rows.append({
            "case": case.id,
            "score": score(case, out),             # exact, rubric, or judge
            "model_resolved": out.model,
            "prompt_version": cfg.prompt_version,
            "ts": utcnow(),
        })
    return aggregate(rows)                          # emit as a normal metric series
```

Chart the score by date, sliced by `llm.model.resolved` and `prompt.version`.
Because the inputs are fixed, a step change cannot be traffic mix, seasonality,
or a new customer segment — it is the dependency or your own change, and the two
slices tell you which. It is also the only artefact that makes a vendor
conversation productive: a dated, reproducible, fixed-input regression is
evidence; "our users say it feels worse" is not.

Keep the probe set honest: refresh perhaps 20% quarterly from real traffic, keep
the hard and the recently-broken cases, and never tune a prompt directly against
it and then declare victory on the same set — at that point you have a training
set, not a monitor. The eval-harness workflow covers how to grow and govern it.

## Common Anti-Patterns

❌ **Model identity not recorded per call.**
✅ Log requested and resolved model plus fingerprint on every span, and alert on resolved changing.

❌ **Floating model aliases in production config.**
✅ Pin dated snapshots; make upgrades a PR gated by the eval suite.

❌ **A log line per API call, with no trace over the user action.**
✅ One trace id across retrieval, tools, retries and generation, exposed as a response id.

❌ **Retries overwriting the original span.**
✅ Emit each attempt as its own span with a retry index and failure reason.

❌ **Cost known only from the provider's monthly bill.**
✅ Compute per-call cost from returned token counts, tagged by feature, step, model, and tenant.

❌ **Tracking mean cost per request.**
✅ Track p50/p95/p99 and alert on the tail — that is where loops and giant documents appear.

❌ **A single p95 latency number.**
✅ Separate TTFT, total duration, and tokens per second; they have different remedies.

❌ **Trusting provider-reported latency.**
✅ Measure end to end from your own edge, including retrieval, retries and guardrails.

❌ **Storing no prompts or completions.**
✅ Capture payloads with redaction at emit — this corpus is your future eval set.

❌ **Storing payloads raw, forever, in the general log index.**
✅ Redact in-process, tier retention, restrict and audit access.

❌ **Random per-span sampling.**
✅ Hash-bucket by trace id so traces stay whole; keep 100% of errors, refusals and tail cost.

❌ **Assessing quality only when someone complains.**
✅ Run a frozen probe set on a schedule and chart it against resolved model and prompt version.

❌ **Treating one proxy metric as quality.**
✅ Watch a panel — schema failures, refusals, retries, regeneration, length, abandonment.

❌ **No cap or counter on agent iterations.**
✅ Record `agent.iteration` and enforce a hard ceiling; alert on the loop-depth distribution.

## LLM Observability Checklist

- [ ] Requested and resolved model, fingerprint, prompt version, and param hash on every call
- [ ] Alert on resolved model changing for a fixed requested model
- [ ] Dated model snapshots pinned in config; deprecation dates on the team calendar
- [ ] One trace per user action spanning retrieval, tools, retries, generation, guardrails
- [ ] Trace id returned to the user and usable to reconstruct the full tree
- [ ] OpenTelemetry GenAI semantic conventions used for attribute names
- [ ] Retries and agent iterations emitted as distinct spans, with a hard loop cap
- [ ] Per-call cost computed in code from a dated rate table in config
- [ ] Cost and tokens tagged by feature, step, model, tenant, and plan
- [ ] p95/p99 cost per request alerted; cost per tenant per day alerted
- [ ] Cache-read share of input tokens tracked as a first-class metric
- [ ] TTFT, total duration, and tokens/sec recorded separately, measured at your edge
- [ ] Prompts, completions, retrieved chunk ids, and tool calls captured with in-process redaction
- [ ] Retention tiers defined for metrics, traces, payloads, and curated eval cases
- [ ] Hash-bucket sampling, with 100% retention of errors, refusals, and tail cost/latency
- [ ] Implicit feedback (regenerate, edit, abandon, escalate) instrumented, not just thumbs
- [ ] Frozen probe set scored on a schedule and charted by model and prompt version
- [ ] Proxy-signal panel dashboarded together, not one metric in isolation
- [ ] Provider retention, training, and subprocessor terms reviewed and recorded
