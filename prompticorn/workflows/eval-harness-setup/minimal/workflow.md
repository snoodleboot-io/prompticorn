---
name: "eval-harness-setup"
description: "Build a golden eval set from real traffic and wire it into CI as a deploy gate"
agent: "mlai"
category: "ml"
related_workflows:
  - prompt-iteration-cycle
  - llm-feature-build
  - rag-pipeline-setup
---

# Eval Harness Setup Workflow

**Problem:** Turn "the outputs look better to me" into a number that blocks a deploy.

The decision that determines whether the harness survives: it must run in CI and be able to fail the build. An eval suite that only runs when someone remembers is a research artefact — it will be stale within a month and nobody will trust the number.

## Steps

### 1. Collect Real Traffic
Eval sets written from imagination test the cases you already handle. Mine production instead: traced requests with inputs, outputs, and any feedback signal.

Sample deliberately rather than randomly:

| Slice | Why | Share |
|---|---|---|
| Typical traffic | The bulk of the distribution | ~40% |
| Thumbs-down, regenerations, edits | Known failures | ~20% |
| Human overrides and escalations | Strong disagreement signal | ~15% |
| Schema failures, refusals, timeouts | Reliability cases | ~10% |
| Tail: longest, shortest, non-English, hostile | Where it breaks | ~15% |

If the feature is not live yet, use historical records of the human-performed task.

### 2. Label a Golden Set
100–300 cases beats 5,000 unreviewed ones. Each case needs an id, an input, an expected output or rubric, tags, and a provenance note.

Two labelling rules:

- **Two labellers on a sample, and measure agreement.** If humans agree only 70% of the time, 70% is your ceiling — and the disagreement usually means your spec is ambiguous, which is a bug in the requirements, not the model.
- **Split dev and held-out at labelling time.** Roughly 70/30. Iteration overfits whatever you read; the held-out slice is the only honest number.

### 3. Pick the Cheapest Scorer That Discriminates
| Scorer | Use when | Cost | Watch out |
|---|---|---|---|
| Exact / set match | Classification, extraction, routing | Free | Brittle on formatting — normalise first |
| Schema + field checks | Structured output | Free | Validity is not correctness |
| Deterministic assertions | "Must cite a real id", "must not contain a phone number" | Free | Underrated; write these first |
| Fuzzy / embedding similarity | Paraphrase-tolerant matching | Cheap | Scores 0.8 for subtly wrong answers |
| LLM judge with a rubric | Open-ended prose | $ and slow | Needs its own validation against humans |
| Human review | The final arbiter | Expensive | Reserve for judge calibration and disputes |

Start deterministic. Most tasks have more checkable structure than they first appear, and a free scorer can run on every commit.

If you use a judge: give it a rubric with concrete levels, ask for the reason before the score, use a pinned model, and validate it against human labels on 50 cases. An unvalidated judge is an opinion generator with a decimal point.

### 4. Wire Into CI as a Gate
```yaml
- name: LLM eval gate
  run: evals run --set dev --fail-under 0.82 --fail-regression 0.03 --report out.json
```

Two thresholds, not one: an absolute floor, and a maximum regression against the last green run on main. The regression check is what catches a change that is still above the bar but two points worse than yesterday.

Gate on prompt changes, model changes, retrieval changes, and dependency bumps. Post the per-tag table as a PR comment so reviewers see *which* cases moved, and make the run reproducible — pinned model snapshot, temperature 0 where supported, fixed seed, frozen case file.

### 5. Track Drift Over Time
The eval suite is also a monitor. Run the full set nightly against the production configuration, and chart the score by date, prompt version, and resolved model id.

A step change on fixed inputs is not traffic mix and not seasonality — it is your change or your provider's. The two slices tell you which. This is the only artefact that makes a vendor conversation productive.

Refresh about 20% of cases quarterly from new traffic, keep hard and recently-broken cases forever, and re-review labels when the spec changes.

## Common Pitfalls

- Eval set written by the same person who wrote the prompt, after the prompt
- Runs only when someone remembers, so it silently rots
- One aggregate score, no per-tag breakdown, so nothing is actionable
- An LLM judge never validated against human labels
- No held-out slice, so a dozen rounds of iteration look like progress
- Absolute floor only, so slow regressions pass
- Non-reproducible runs (floating model alias, non-zero temperature) that flap
- Cases fixed at launch and never refreshed as traffic changes
