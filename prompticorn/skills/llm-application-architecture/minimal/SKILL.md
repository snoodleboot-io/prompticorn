# LLM Application Architecture (Minimal)

## Purpose
Build an LLM feature that stays inside a latency and cost budget under real traffic, and degrades into something useful when the model is slow, rate-limited, or wrong.

## Core Techniques

### 1. Pick Two Corners of the Triangle, Per Call Site
Latency, cost, and quality trade against each other. There is no global answer — only a per-call-site answer.

| Call site | Optimize for | Give up | Typical shape |
|---|---|---|---|
| Inline autocomplete | Latency | Quality | Small model, short context, no tools, streamed |
| User-facing chat | Latency + quality | Cost | Large model, prompt caching, streamed |
| Bulk classification | Cost | Latency | Small model, batched, buffered |
| Contract or code review | Quality | Latency + cost | Large model, long context, multi-pass |

Write the budget down as a number before you write the prompt: "p95 under 2s, under $0.004 per request." A feature without a budget defaults to the largest model and the longest context, and nobody notices until the invoice or the p95 does.

### 2. Budget the Context Window Like a Fixed Allocation
The window is a hard limit shared by system prompt, retrieved documents, conversation history, tool definitions, and the completion. Assign each a cap and enforce it in code.

```python
BUDGET = {"system": 1_000, "tools": 1_500, "retrieved": 6_000,
          "history": 4_000, "reserve_for_output": 2_000}

def assemble(system, tools, docs, history, limit):
    parts = [system, tools]
    parts.append(truncate_docs(docs, BUDGET["retrieved"]))        # drop lowest-ranked whole docs
    parts.append(trim_history(history, BUDGET["history"]))        # drop oldest whole turns
    assert count_tokens(parts) + BUDGET["reserve_for_output"] <= limit
    return parts
```

Two rules that prevent most window bugs: never truncate mid-document or mid-turn (drop whole units, lowest value first), and always reserve output tokens. Running out of window mid-generation produces a truncated response that looks like a model quality problem and is not.

### 3. Stream When a Human Reads It, Buffer When a Program Does
| | Stream | Buffer |
|---|---|---|
| Consumer | Human reading prose | Parser, schema validator, downstream call |
| Wins | Time-to-first-token, perceived speed | Validate before anyone sees it; retry invisibly |
| Costs | Cannot validate or retry after bytes have shipped | Full generation latency is felt |

Streaming is a UX decision, not a performance one — total tokens and total cost are identical. The trap is streaming structured output: once half a malformed JSON object is on the wire, you cannot retry without visibly retracting. Buffer anything you intend to parse.

### 4. Route Cheap First, Escalate on a Signal
Most traffic is easy. Send it to the small model, and promote only what needs promoting.

```python
result = small_model(prompt)
if result.confidence < 0.7 or result.refused or validation_failed(result):
    result = large_model(prompt)     # escalate
```

The escalation signal must be cheap and honest. A self-reported "confidence: 0.9" from the model is neither. Prefer structural signals: schema validation failed, the classifier returned `unknown`, a required field is missing, the retrieval scores were all low. Measure the escalation rate — if it is above ~30%, the two-model path costs more than going large directly, because you pay for both.

### 5. Cache at Two Different Layers
| | Prompt cache | Semantic cache |
|---|---|---|
| Keys on | Exact token prefix | Embedding similarity of the request |
| Saves | Cost and latency of re-reading a long prefix | The entire call |
| Risk | None — output is unaffected | Returns an answer to a *similar* question |
| Use for | Long stable system prompts, few-shot blocks, large documents reused across turns | Repeated FAQ-shaped questions |

Prompt caching is nearly free to adopt and rewards putting everything static at the front of the prompt, in a byte-stable order. Semantic caching is where the correctness bugs live: "cancel my order" and "can I cancel my order?" are near-identical embeddings and require different answers. Gate it on a high similarity threshold, scope the key by user and tenant, and never cache a response that consumed personalized context.

### 6. Name the Four Failure Modes and Give Each a Fallback
| Failure | Signal | Graceful degradation |
|---|---|---|
| Timeout | No token within the deadline | Return partial stream, or cached/templated answer |
| Truncation | Stop reason is "length" | Reserve output tokens; retry with shorter input, not a longer budget |
| Rate limit | 429 | Backoff with jitter, then shed to the small model or a queue |
| Malformed output | Schema validation fails | One repair retry, then a deterministic non-LLM path |

Every LLM call needs a defined answer to "what does the user see when this does not return?" The default — a spinner until the gateway times out — is a choice nobody made deliberately.

## Warning Signs

- No stated latency or cost budget for the call site
- Context assembled by concatenation with no token accounting, and no reserved output tokens
- Structured output streamed to the client and parsed as it arrives
- One model for every call site regardless of difficulty
- Escalation gated on the model's self-reported confidence
- Volatile content (timestamps, user names) at the front of the prompt, defeating the prefix cache
- Semantic cache keyed globally rather than per user or tenant
- Retries on timeout with no jitter and no overall deadline, so a slow upstream becomes a retry storm
- Cost measured monthly in aggregate instead of per request per feature
