# LLM Evaluation and Testing (Minimal)

## Purpose
Put a number on the quality of a non-deterministic system so a prompt change, a
retrieval change, or a model upgrade can be accepted or rejected on evidence
rather than on whether the last three outputs looked good.

## Core Techniques

### 1. Build the Eval Set From Real Traffic
You cannot improve what you cannot score, and "it looks better" does not survive a
model upgrade. The first artifact is a fixed set of inputs you will re-run forever.

Sample from production logs, not imagination. Stratify deliberately:

| Slice | Share | Why it is in the set |
|---|---|---|
| Head — the most common request shapes | ~40% | Regressions here are user-visible immediately |
| Tail — rare, long, multi-part requests | ~25% | Where models differ most |
| Known failures — every reported bug | ~20% | Each one becomes a permanent test |
| Adversarial — injection, off-topic, refusal bait | ~10% | Safety behaviour is a property to hold, not hope for |
| Empty and malformed input | ~5% | The cases nobody writes by hand |

100–300 cases is enough to start and is roughly the volume a human can label in a
day. Freeze it, version it in git alongside the prompts, and add to it every time
something breaks in production. Do not edit a case to make a score go up.

### 2. Know Which of the Two Scoring Regimes You Are In
| | Reference-based | Reference-free |
|---|---|---|
| Needs | A correct answer per case | A rubric or a checkable property |
| Examples | Exact match, F1 on extracted fields, ROUGE against a gold summary | Faithfulness to context, tone, schema validity, refusal correctness |
| Strength | Cheap, deterministic, trustworthy | Works where no single answer is right |
| Weakness | Only exists for tasks with one right answer | Needs a judge, and judges have biases |

Extraction, classification, and routing are reference-based — assert on them like
ordinary code. Summarization, chat, and open generation are reference-free. Most
systems contain both, and the mistake is scoring one regime with the other's tools.

### 3. Assert on Properties, Not on Strings
Exact matching breaks on non-deterministic output: same input, same prompt,
different wording, test red. Assert what must be true instead.

```python
def test_extracts_invoice(agent):
    out = agent.run(INVOICE_TEXT)
    assert out.schema_valid                       # deterministic
    assert out.total == Decimal("1284.50")        # deterministic
    assert out.currency == "USD"                  # deterministic
    assert 0 < len(out.line_items) <= 20          # bounded, not exact
    assert "1284.50" in out.summary               # substring, not equality
```

Push structure into the output format so the deterministic assertions carry most
of the weight. A tool call, a JSON schema, or an enum is testable; a paragraph is
not. What genuinely cannot be pinned down goes to a judge — and that should be
the minority of your assertions, not the default.

### 4. Use an LLM Judge, and Correct for Its Known Biases
| Bias | Symptom | Mitigation |
|---|---|---|
| Position | In A/B comparison the first (or last) option wins disproportionately | Run both orders, keep only agreeing verdicts, count disagreements as ties |
| Self-preference | A judge scores text from its own model family higher | Use a different model as judge than the one under test |
| Verbosity | Longer answers score higher regardless of content | Include length in the rubric, or truncate both to comparable length |
| Scale compression | Nearly everything is a 7 or 8 out of 10 | Use binary or 3-point criteria, several of them, rather than one 1–10 score |
| Leniency | Judge accepts anything plausible | Anchor with few-shot examples of failing outputs, not just passing ones |

Then validate the judge itself: label 50 cases by hand, measure agreement with the
judge, and only trust the judge where agreement is high. An unvalidated judge is an
unmeasured instrument, and its scores are decoration.

### 5. Gate Deploys on a Regression Suite
```yaml
- name: eval
  run: python -m evals run --suite regression --out results.json
- name: gate
  run: |
    python -m evals gate results.json \
      --fail-under accuracy=0.92 \
      --fail-under faithfulness=0.95 \
      --no-regression-on tests/evals/must_pass.jsonl \
      --max-p95-latency-ms 4000 \
      --max-cost-per-case-usd 0.02
```

Two thresholds, not one. An aggregate floor catches broad degradation; a
must-pass list of previously-fixed bugs catches the specific regression that
aggregate accuracy hides. Record cost and latency in the same run — a prompt
change that gains one accuracy point and triples token spend is a decision, and
it needs both numbers to be made.

### 6. Re-Run the Whole Suite on Every Model Change
A model upgrade is not a drop-in. Prompts tuned against one model's quirks
frequently regress on another, output formatting shifts, refusal boundaries move,
and tool-calling behaviour changes. Pin the model version in config, run the full
suite on the candidate, and compare per-case rather than only in aggregate — the
interesting information is the list of cases that flipped in each direction.

## Warning Signs

- Quality assessed by reading a handful of outputs after each change
- No eval set, or one written from imagination rather than sampled from traffic
- Test cases edited when they fail instead of being investigated
- Exact string equality asserted against free-form generated text
- A judge from the same model family as the system under test
- Judge agreement with human labels never measured
- Single 1–10 quality score with no rubric, no examples, and no anchors
- Pairwise comparisons run in one order only
- Deploys gated on aggregate accuracy with no must-pass regression list
- Cost and latency not recorded alongside quality
- Model version floating rather than pinned, so quality changes arrive unannounced
- Production failures fixed in the prompt but never added to the eval set
