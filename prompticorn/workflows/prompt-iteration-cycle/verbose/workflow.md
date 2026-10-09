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

**Problem:** Improve a prompt without a two-week detour in which the score ends lower than it started and nobody can say which of the eleven edits did it.

The governing idea: **a prompt is production code that happens to be written in English.** It gets a version, a diff, a review, a test run, and a rollback path. The reason teams do not treat it that way is that it is editable in a text box — which is also the reason prompt regressions ship on Friday afternoons with no record of what changed.

The second idea, which is what makes the loop converge: change one variable per round. This feels slow. It is dramatically faster than the alternative, because a round that changes three things and moves the score by four points teaches you nothing, and the team will usually keep all three — including the one that made things worse.

## Steps

### 1. Measure the Baseline First

Run the current prompt against the dev eval set and record the number, the per-tag breakdown, and the cost and latency. Before editing anything.

```bash
evals run --set evals/dev.jsonl --prompt triage/v7 \
          --model-snapshot "$PINNED" --temperature 0 --report baselines/v7.json
```

```
triage/v7 — dev (n=210)
overall       0.812
├─ typical    0.940
├─ ambiguous  0.510      ← the entire deficit lives here
├─ adversarial 0.950
├─ long_input 0.680
└─ non_english 0.790
schema_valid 0.995 | refusal 0.014 | p95 1.8s | $0.0029/case
```

The headline number invites aimless tinkering. The breakdown names a problem: two tags are dragging the average while the common path is fine. Optimising `typical` from 0.94 upward is where teams instinctively spend time and where the remaining points are not.

**Establish your noise floor now, once.** Run the identical configuration three to five times and measure the spread.

```bash
for i in 1 2 3 4 5; do evals run --set evals/dev.jsonl --prompt triage/v7 --quiet; done
# 0.812 0.807 0.815 0.809 0.812   → spread ≈ 0.008
```

Every subsequent decision depends on this number. A change of 0.006 on a suite with a 0.008 spread is not a result, and treating it as one is how teams accumulate a dozen neutral changes and a prompt nobody understands. If the spread is large, reduce it before iterating: temperature 0 where supported, a pinned model snapshot, a fixed seed if offered, and more cases (at n=50 a single flipped case moves the score 2 points).

### 2. Form a Hypothesis From Actual Failures

Read 10–20 failing cases before changing a word. Prompt editing driven by intuition about what the model "probably needs to hear" burns rounds; the failure category almost always names the fix.

```bash
evals run --set evals/dev.jsonl --prompt triage/v7 --report r.json
evals failures r.json --tag ambiguous --limit 15 --show input,expected,actual
```

| Observed failure | Root cause | The change that works |
|---|---|---|
| Right substance, wrong shape | Output contract underspecified | Tighten the schema; show one formatted example |
| One class consistently confused with another | **Your own definition is ambiguous** | Write the boundary rule and a contrastive pair |
| Asserts facts absent from the input | Missing knowledge | Retrieval (`rag-pipeline-setup`) — not prompt wording |
| Correct but three times too long | No length constraint | State the limit and enforce with `max_tokens` |
| Refuses legitimate requests | Over-broad safety framing | Name the in-scope domain explicitly; narrow the prohibition |
| Ignores a rule stated mid-prompt | Placement | Move critical rules to the end; number them |
| Degrades on long inputs | Instructions buried under content | Instructions after the content, not before it |
| Inconsistent across identical inputs | Temperature, or a genuinely ambiguous case | Lower temperature; check the label first |

Row two deserves emphasis because it is the most common and the least often diagnosed. When the model cannot reliably distinguish "bug" from "feature request," the usual reason is that your team cannot either — the spec never said. No prompt phrasing fixes an undefined boundary. If inter-annotator agreement on that tag was 65%, the model is performing at the ceiling and the work is a product decision, not a prompting one.

Write the hypothesis down before editing:

> *Ambiguous bug-vs-feature cases fail because the prompt never states which wins when a report describes existing behaviour the user dislikes. Adding an explicit tiebreak rule should lift the `ambiguous` tag by ~0.15 and leave other tags flat.*

A written prediction turns each round into an experiment with a result. It also stops the most common time sink: fixing something the failures did not show.

### 3. Change One Variable

```bash
cp prompts/triage/v7.md prompts/triage/v8.md
# v8 adds exactly one thing: the bug-vs-feature tiebreak rule
```

One edit per round. Not wording plus temperature. Not a new example plus a model swap. Not "a few small cleanups while I'm in here."

| Variable | Typical effect size | Notes |
|---|---|---|
| Clarifying an ambiguous definition | Large | Usually the highest-yield single change |
| Adding 3–5 few-shot examples | Large on format and edge cases | Choose examples that cover failure modes, not typical cases |
| Reordering — rules last, content first | Moderate, especially on long inputs | Cheap to try |
| Tightening the output schema | Moderate; removes parse failures | Free at runtime |
| Adding an explicit "if unsure" path | Moderate; converts wrong answers to routable ones | |
| Decomposing into two calls | Moderate on multi-part tasks | Costs latency and money |
| Temperature / sampling params | Small, except for consistency | Change alone, never with wording |
| Model or snapshot | Variable, sometimes large | **Always its own round** |

Model changes especially must be isolated. Changing the model and the prompt together and seeing +0.04 leaves you unable to answer whether the prompt edit helped, hurt, or was cancelled out — and you will carry that uncertainty forward into every later round.

When the hypothesis calls for examples, pick them from the failures you just read, and include at least one near-miss contrastive pair — two similar inputs with different correct answers. Examples covering cases the model already handles add tokens and change nothing.

### 4. Re-Score Against the Eval Set

Same set, same model snapshot, same temperature, same seed, same scorer version. If more than the prompt changed, the comparison is invalid.

```bash
evals compare --baseline baselines/v7.json \
              --candidate <(evals run --set evals/dev.jsonl --prompt triage/v8 --json)
```

```
                 v7      v8       Δ      noise floor ±0.008
overall        0.812   0.847   +0.035    ✓ real
├─ ambiguous   0.510   0.690   +0.180    ✓ hypothesis confirmed
├─ typical     0.940   0.935   -0.005    – within noise
├─ adversarial 0.950   0.950    0.000    –
├─ long_input  0.680   0.610   -0.070    ✗ real regression
└─ non_english 0.790   0.795   +0.005    –
cost/case     $0.0029 $0.0034  +17%      ← the new rule costs tokens
p95 latency     1.8s    1.9s   +0.1s
```

Three habits here separate a converging loop from a random walk.

**Always check the other tags.** Prompt changes have side effects: a rule added for one case fires on another; a new example shifts the format for everything; extra instructions push content further from the model's attention. The `long_input` drop above is a real finding, and it needs diagnosis — read the new failures, do not average them away.

**Compare against the noise floor, not against zero.** `-0.005` on `typical` is nothing. `-0.070` on `long_input` is nine times the spread and is a fact.

**Track cost and latency in the same table.** A +0.035 quality gain for +17% cost is a decision someone should make deliberately. Reported alone, quality gains always look free, and a quarter later the unit economics are someone else's problem.

For a change that looks marginal, one more run of each configuration usually resolves it faster than an argument. If it is still marginal after that, it is marginal — reject it and keep the simpler prompt.

### 5. Keep or Revert, Then Commit the Prompt Like Code

**Keep** on a gain clearly above the noise floor, with no unexplained regression on another tag, at an acceptable cost delta.

**Revert** otherwise — including changes that read better, feel more thorough, or that someone spent an afternoon on. This step is the one that makes the difference, and it is the one teams skip. A prompt accretes neutral-but-plausible instructions round after round until it is 3,000 tokens of accumulated superstition that nobody dares remove because nobody knows which parts matter.

Periodically run the reverse experiment: delete a paragraph and re-score. Instructions that contribute nothing are not free — they cost tokens, they dilute attention, and they make every future change harder to reason about.

```
prompts/
  triage/
    v7.md
    v8.md            ← current
    CHANGELOG.md
```

```markdown
## v8 — 2026-09-12
Adds a bug-vs-feature tiebreak rule ("describes existing behaviour the user
dislikes → feature_request").
Hypothesis: lifts `ambiguous`, leaves other tags flat.
Result: dev 0.812 → 0.847. ambiguous +0.18 (confirmed).
  long_input -0.07 — traced to the added example pushing the rules block
  past 6k tokens on the longest cases. Accepted; tracked as PRO-xxx.
Cost: $0.0029 → $0.0034/case (+17%).
Held-out: not yet re-checked (last check at v6: dev +0.06 → held-out +0.02).
```

Then treat it as code in every respect: prompts live in the repo, changes go through a PR, and the reviewer — someone who did not write it — checks the eval delta, the regression analysis, and the cost, not the English prose style. Prompts stored in a database or an admin dashboard have no diff, no review, and no history, which means a production behaviour change can happen with no record at all.

One non-negotiable: emit the prompt version on every request.

```python
span.set_attribute("llm.prompt.version", PROMPT_VERSION)   # "triage/v8"
```

Without it, a production complaint cannot be tied to a prompt version, and your nightly quality chart cannot separate your changes from the provider's.

### 6. Roll Out With a Rollback Path

A prompt change is a behaviour change to a live system. It gets the same rollout machinery as code.

```yaml
prompts:
  ticket_triage:
    active: "triage/v8"
    previous: "triage/v7"        # rollback target, still deployed
    rollout_percent: 10
    bucket_by: tenant_id         # stable assignment — no flapping between versions
    kill_switch: true            # reverts to `previous` without a deploy
```

Ramp 10% → 50% → 100%, and watch the production proxies at each step, because your eval set is a few hundred cases and production is not:

- Schema failure and parse error rate
- Refusal rate — a tightened instruction very often over-refuses, and the eval set may not contain the affected cases
- Retry rate, tool-error rate in agent flows
- Regeneration and edit rate; human override rate
- Output length distribution — a good early tell that behaviour moved
- Cost per request at p95 and p99

Roll back first, diagnose second. A prompt rollback should take seconds; if it requires a deploy and a build, that is worth fixing before the next iteration round rather than during the next incident.

Hold the model snapshot fixed across a prompt rollout. Rolling a prompt and a model upgrade in the same week gives you two candidate causes for any production movement and no way to separate them — the same mistake as step 3, at a larger blast radius.

### 7. Check the Held-Out Set Before Declaring Victory

Every round of iteration fits the prompt a little more tightly to the cases you have been reading. This is not occasional; it is the default outcome. After a batch of accepted changes — every 5–10 rounds, or before any significant ship decision — score the held-out slice.

```bash
evals run --set evals/heldout.jsonl --prompt triage/v8 --report heldout/v8.json
```

```
              dev      held-out
v7           0.812      0.795
v8           0.847      0.812
Δ           +0.035     +0.017     ← roughly half the gain was overfit
```

That gap is normal and is exactly what the held-out set is for. What matters is its size. A dev gain of +0.08 alongside a held-out gain of +0.01 means you spent the week learning the dev set's idiosyncrasies, and the honest response is to refresh the dev set with new traffic rather than to keep iterating.

Two rules protect this number. **Do not read held-out failures and edit the prompt in response** — the moment you do, it is a second dev set and you have no unbiased estimate left. And **do not check it every round**; repeated peeking leaks information into your decisions even without deliberate tuning.

When the dev score approaches your measured inter-annotator agreement, stop. The suite has stopped discriminating, remaining "gains" are fitting labeller noise, and the next real improvement comes from a clearer spec, better retrieval, or a different model — not from more prompt rounds. `eval-harness-setup` covers refreshing the sets when that point is reached.

## Common Pitfalls

- **Editing before reading failures.** Intuition about what the model needs to hear is a poor predictor; the failures name the fix.
- **Multiple changes per round.** The score moves and the cause is unattributable — and the harmful change gets kept along with the helpful one.
- **Judging by reading a handful of outputs.** Recency and confirmation bias do the rest; this is the failure mode the whole workflow exists to prevent.
- **Chasing differences inside the noise floor.** Half the accepted changes are then coin flips.
- **Keeping changes that read better but score the same.** Prompt bloat accretes, tokens cost money, and future changes get harder to reason about.
- **Never deleting anything.** Nobody knows which instructions still matter, so nothing is ever removed.
- **Changing model and prompt together.** Two candidate causes, no conclusion.
- **Prompts in a database or dashboard.** No diff, no review, no history, no rollback.
- **Prompt version absent from traces.** A production complaint cannot be tied to a version, and drift cannot be attributed.
- **Prompt rollout with no percentage and no kill switch.** A behaviour change goes to 100% of users in one step.
- **Tightening an instruction without watching refusal rate.** Over-refusal ships, and the eval set does not contain the cases it breaks.
- **Never checking the held-out set.** The reported improvement is mostly overfit and nobody knows by how much.
- **Tuning against the held-out set once it is checked.** The last honest measurement in the system is spent.

## Related Workflows

- [Eval Harness Setup](../eval-harness-setup) — the scored suite and the dev/held-out split this loop assumes
- [LLM Feature Build](../llm-feature-build) — where this loop sits in the overall build
- [RAG Pipeline Setup](../rag-pipeline-setup) — when the failures point at missing knowledge rather than prompt wording
