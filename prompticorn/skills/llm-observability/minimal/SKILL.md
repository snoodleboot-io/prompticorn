# LLM Observability (Minimal)

## Purpose
Know what your LLM feature costs, how slow it is, and when its quality moved — on a system with no ground truth and a dependency whose behaviour can change without a deploy on your side.

## Core Techniques

### 1. Instrument on the Assumption That the Model Will Change Underneath You
The model is a dependency you do not control and, by default, cannot version-pin. A floating alias silently rolls forward; a provider tunes serving; a snapshot is deprecated with a migration window. None of these produce a diff in your repo, a failed build, or a 500. Your telemetry is the only place the change becomes visible.

So two things go on every span, always:

```python
span.set_attributes({
    "llm.model.requested": requested_model,        # what your config asked for
    "llm.model.resolved":  response.model,         # what the provider actually ran
    "llm.prompt.version":  PROMPT_VERSION,         # your own git-tracked prompt id
    "llm.params.hash":     hash_params(params),    # temperature, top_p, max_tokens
})
```

Alert on `llm.model.resolved` changing value for a fixed `llm.model.requested`. That alert is the one that turns "quality mysteriously dropped three weeks ago" into a dated, attributable event.

### 2. Trace the Request, Not the Call
One user action is rarely one model call. Retrieval, a tool round-trip, a retry, a summarisation pass, a judge — a per-call log tells you nothing about which of them was slow, expensive, or wrong.

```
span: chat.request           user=u_913  feature=support_copilot  4.8s  $0.031
 ├─ retrieve                 k=8  hits=8  recall_proxy=0.75        180ms
 ├─ llm.generate  step=plan  in=2,140 out=96   cached_in=1,900     640ms
 ├─ tool.lookup_order        status=ok                              90ms
 ├─ llm.generate  step=answer in=4,820 out=412 cached_in=1,900    3,700ms  ← 77%
 └─ guardrail.output         verdict=pass                            25ms
```

Propagate one `trace_id` through the whole action and stamp it on every log line and every user-visible response id. When a user reports a bad answer, the id they quote must retrieve the entire tree — prompts, retrieved chunk ids, tool arguments, and the raw completion.

### 3. Account Cost at the Span, Not at the Invoice
A monthly provider bill is unattributable. Compute cost in your own code from the token counts each call returns, and tag it with the dimensions you will actually be asked about.

```python
cost = (
    usage.input_tokens         * rate.input
  + usage.cache_write_tokens   * rate.cache_write
  + usage.cache_read_tokens    * rate.cache_read     # typically far cheaper
  + usage.output_tokens        * rate.output         # typically the priciest per token
)
emit("llm.cost_usd", cost, tags={"feature": f, "step": s, "model": m,
                                 "tenant": t, "user_bucket": bucket(user_id)})
```

Keep the rate table in config with an effective date, never inline in code. Then watch the distribution, not the mean: LLM spend is heavy-tailed, and p99 cost per request is what a runaway agent loop or a 200-page pasted document looks like before it reaches finance. Alert on cost per request and per tenant per day, not on the monthly total.

### 4. Split Latency Into Its Two Honest Numbers
| Metric | Measures | Use it for |
|---|---|---|
| Time to first token | Queue + prompt processing + retrieval before it | Perceived speed of a streamed UI |
| Total duration | TTFT + output length ÷ generation rate | Anything a program consumes; timeouts |
| Output tokens per second | Generation throughput | Separating "provider is slow" from "we asked for 2,000 tokens" |

Reporting only p95 total merges two unrelated causes. TTFT rising means queueing, a longer prompt, or slow retrieval; total rising with flat TTFT means you are simply generating more. The fix differs: shorten or cache the prompt versus constrain the output.

Measure end-to-end from your own edge. Provider-reported latency excludes your retrieval, your retries, and your guardrails, which is usually where the time went.

### 5. Capture Inputs and Outputs — They Are Your Future Eval Set
Aggregates tell you something changed; only the payloads tell you what. Store the resolved prompt, the completion, retrieved chunk ids, tool calls, and any user feedback signal. This corpus is where a golden eval set comes from; without it you are writing test cases from imagination.

Make that compatible with privacy rather than choosing between them:

| Control | Practice |
|---|---|
| Redact at emit | Scrub secrets and unneeded PII before the payload leaves the process — never in the sink |
| Tier retention | Metrics 13 months, traces 30 days, full payloads 7–14 days, curated eval cases indefinitely with consent |
| Sample deliberately | Hash-bucket by trace id so a request is fully present or fully absent; keep 100% of errors, refusals, thumbs-down, and top-decile cost |
| Restrict access | Payload stores are production data; access-controlled and audited |

### 6. Detect Quality Drift Without Ground Truth
You cannot compute accuracy on live traffic. You can watch a panel of proxies that move when quality moves, and run a fixed probe set on a schedule.

Proxies, cheapest first: schema validation failure rate; guardrail block and refusal rate; retry rate; tool-call error rate; output length distribution; user regeneration or edit rate; thumbs-down rate; conversation abandonment; escalation to a human.

The probe set is the definitive part. Take 50–200 frozen prompts with known-good outputs, run them hourly or nightly against production config, score them, and chart the score by date and by `llm.model.resolved`. A step change on a fixed input set is not noise and not your users — it is the dependency moving. This is also the only artefact that lets you prove it to a vendor.

## Warning Signs

- Model identity not recorded per call, so a silent version change is undetectable
- Per-call logs with no trace linking the steps of one user action
- Cost known only from the provider's monthly bill
- No cost or token attribution per feature, tenant, or user
- Latency reported as a single p95 with TTFT and total conflated
- Prompts and completions never stored, so every eval set is written from scratch
- Payloads stored raw and indefinitely, with no redaction and no retention tier
- Sampling that keeps a random subset of spans, breaking trace reconstruction
- Quality assessed only by reading outputs when someone complains
- No scheduled probe set, so drift is attributed to "the prompt" for weeks
- No alert on cost per request, so a retry loop is discovered at month end
