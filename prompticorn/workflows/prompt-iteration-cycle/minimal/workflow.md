---
name: "prompt-iteration-cycle"
description: "Change a prompt one variable at a time, re-score it, and version it like code"
agent: "mlai"
category: "ml"
related_workflows:
  - eval-harness-setup
  - llm-feature-build
  - rag-pipeline-setup
---

# Prompt Iteration Cycle Workflow

**Problem:** Improve a prompt without a two-week detour in which the score goes down and nobody can say which of the eleven edits did it.

The governing rule: a prompt is production code that happens to be written in English. It gets a version, a diff, a review, a test run, and a rollback path. The fact that it is editable in a text box is the reason teams treat it as configuration — and the reason regressions ship on Friday afternoons.

## Steps

### 1. Measure the Baseline First
Before touching anything, run the current prompt against the eval set and record the number with its per-tag breakdown. No baseline means no way to distinguish improvement from motion.

```bash
evals run --set dev --prompt triage/v7 --report base.json
# overall 0.812 | typical 0.94 | ambiguous 0.51 | long_input 0.68 | n=210
```

Read the tags, not the headline. `0.812` suggests vague prompt tweaking; "ambiguous is at 0.51 and everything else is above 0.9" is one specific problem to solve.

### 2. Form a Hypothesis From Actual Failures
Read 10–20 failing cases before editing a single word. The fix follows from the failure category, and guessing wastes rounds:

| What you see in failures | Likely cause | Change |
|---|---|---|
| Right idea, wrong format | Underspecified contract | Tighten the schema; add a format example |
| Consistent misclassification of one class | Your definition is ambiguous | Define the boundary explicitly; add a contrastive example |
| Facts not in the input | Missing context | Retrieval or input expansion, not prompt wording |
| Correct but far too long | No length constraint | Cap it, and enforce with `max_tokens` |
| Refusals on legitimate cases | Over-broad safety framing | Narrow the prohibition, name the in-scope domain |
| Ignores an instruction buried mid-prompt | Instruction placement | Move it to the end; make it a named rule |

Write the hypothesis down: "ambiguous bug-vs-feature cases fail because the prompt never says which wins; adding a tiebreak rule should move the `ambiguous` tag."

### 3. Change One Variable
One edit per round. Not prompt wording plus temperature. Not a new example plus a model swap. When two things change and the score moves, you have learned nothing and will likely keep the wrong one.

```
prompts/triage/v8.md   (v7 + explicit bug-vs-feature tiebreak rule)
```

### 4. Re-Score Against the Eval Set
Same set, same model snapshot, same temperature, same seed. Compare per tag, and always check that other tags did not drop.

```
              v7      v8     Δ
overall     0.812   0.847  +0.035
ambiguous   0.510   0.690  +0.180   ← the hypothesis held
typical     0.940   0.935  -0.005   ← within noise
long_input  0.680   0.610  -0.070   ← a real regression, investigate
```

Know your noise floor: run the same config three times and measure the spread. A change smaller than that spread is not a result. And keep an eye on cost and latency — a longer prompt with more examples buys quality with tokens.

### 5. Keep or Revert, Then Commit the Prompt Like Code
Keep only on a clear win with no unexplained regression. Otherwise revert — including reverting changes that "feel" better. This is the step that actually distinguishes this workflow from tinkering.

```
prompts/
  triage/
    v7.md
    v8.md          ← current
    CHANGELOG.md   # v8: bug-vs-feature tiebreak. dev 0.812→0.847. ambiguous +0.18.
                   #     long_input -0.07, traced to the new example's length. Accepted.
```

Prompts go in git, in a PR, reviewed by someone who did not write them, with the eval delta in the description. The reviewer's job is to check the claim, not to read the English for style.

### 6. Roll Out With a Rollback Path
Ship the prompt version behind the same flag mechanism as code: a percentage rollout, a pinned model snapshot, and a switch that reverts to the previous version without a deploy.

Watch production proxies for the first hours — schema failures, refusal rate, regeneration rate, human overrides, cost per request at p99. Roll back on a proxy moving, then diagnose. A prompt rollback should be seconds, not a release cycle.

### 7. Check the Held-Out Set Before Declaring Victory
Every round of iteration overfits the set you are reading. After a batch of accepted changes, score the held-out slice. If the dev gain was 8 points and the held-out gain is 2, most of what you "fixed" was the dev set. That is normal, and knowing the size of the gap is the point.

## Common Pitfalls

- Editing the prompt before reading the failing cases
- Several changes per round, so the cause of a move is unknowable
- Judging by reading a handful of outputs instead of re-scoring
- Keeping a change that reads better but scores the same
- Chasing differences smaller than the measurement noise
- Prompts living in a database or a dashboard with no diff, review, or history
- No prompt version recorded in traces, so a production issue is untraceable
- Never checking the held-out set, so the reported gain is mostly overfit
