---
name: "llm-feature-build"
description: "Take an LLM feature from scope to shipped behind a flag, with an eval set written before the prompt"
agent: "mlai"
category: "ml"
related_workflows:
  - eval-harness-setup
  - prompt-iteration-cycle
  - rag-pipeline-setup
---

# LLM Feature Build Workflow

**Problem:** Ship an LLM feature you can measure, price, and roll back — instead of a demo that worked on the six examples someone tried by hand.

The ordering decision that separates the two: the eval set is written *before* the prompt. Write the prompt first and every subsequent judgement about it is an opinion, because you have no fixed input set to compare against.

## Steps

### 1. Scope to a Task With a Checkable Answer
State the job in one sentence with a verb: classify, extract, rewrite, summarise, route, draft. If the sentence needs "and," it is two features — build the first one.

Then answer three questions before anything else, because they change the architecture:

| Question | If the answer is... | Consequence |
|---|---|---|
| Is the answer checkable? | No — open-ended prose | You need human or judge scoring, and a slower loop |
| Does it need private knowledge? | Yes | Retrieval (see `rag-pipeline-setup`), not a longer prompt |
| What does a wrong answer cost? | A lot | Human confirmation, narrow scope, conservative launch |

Write the budget as numbers now: p95 latency, cost per request, and the quality bar you will ship at. A feature without numbers ships on the largest model with the longest context and nobody notices until the invoice.

### 2. Define the Output Contract Before the Prompt
Decide the exact shape the rest of the system consumes. Structured output where anything parses it; prose only where a human reads it.

```python
class Triage(BaseModel):
    category: Literal["billing", "bug", "feature_request", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(max_length=200)
    confidence: Literal["high", "low"]     # a routing signal, not a probability
```

Decide the failure path here too: what happens on unparseable output, a refusal, a timeout, a rate limit. "Retry twice, then fall back to the existing rules engine and flag for review" is a design decision, not an implementation detail.

### 3. Build the Eval Set Before You Write the Prompt
Aim for 50–100 cases to start. Sources, in order of value: real traffic or real historical records, edge cases from whoever does the job today, and known-bad inputs (empty, hostile, wrong language, enormous, ambiguous).

Every case gets an input, an expected output or a rubric, and a tag. Hold out a slice you do not look at while iterating. Details in `eval-harness-setup`.

### 4. Implement the Thinnest Version That Runs End to End
One model call, a plain prompt, schema validation, the fallback path, and full tracing from the first commit. No routing, no caching, no agent loop, no fine-tuning. You are establishing a baseline number, not a product.

### 5. Measure the Baseline, Then Iterate One Variable at a Time
Score the thin version against the eval set. That number is the reference every later change is judged against — including the decision not to ship. Improve with `prompt-iteration-cycle`: one change, re-score, keep or revert.

Optimise cost and latency only after the quality bar is met. Shrinking the model before you know what "good" is means you cannot tell whether the cheap version is worse.

### 6. Ship Behind a Flag, at a Percentage
Launch to 1–5% of traffic with the fallback still wired in. Watch quality proxies (schema failures, refusals, regenerations, escalations) and cost per request at p99, not the mean. Ramp on evidence.

Pin an explicit model snapshot rather than a floating alias, so an upgrade is a PR gated by the eval suite rather than a surprise. Instrument per `llm-observability` before the first percent, not after the first incident.

## Common Pitfalls

- Prompt written first, eval set retrofitted to the prompt's current behaviour
- Demo built on the six inputs the author happened to try
- No fallback, so a provider incident is a feature outage
- Free-text output that a downstream parser has to guess at
- Cost and latency optimised before the quality bar is established
- Shipped at 100% because it "worked in staging"
- Floating model alias in production config
