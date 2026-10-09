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

One decision determines whether this harness is still used in six months: **it has to run in CI and be able to fail the build.** An eval suite that runs when someone remembers to run it is a research artefact. It goes stale within a month, the number stops matching anyone's intuition, and the team quietly returns to eyeballing outputs — which is where they started, only now with a folder of unused JSON.

The second decision is almost as consequential: start deterministic. Teams reach for an LLM judge immediately because the task "feels subjective," and end up with a slow, expensive, uncalibrated scorer they cannot run on every commit. Most tasks contain far more checkable structure than they appear to.

## Steps

### 1. Collect Real Traffic

Eval sets written from imagination test the cases you already handle well, because the author's mental model of the task is the same mental model that produced the prompt. The corpus has to come from outside that loop.

If the feature is live, mine your traces — which assumes you captured prompts, completions, and feedback signals in the first place (see `llm-observability`). If it is not live, use historical records of the human-performed task: past tickets and their resolutions, past extractions, past routing decisions.

**Sample deliberately, not randomly.** A random sample of production traffic is mostly easy cases, and an eval set that is 90% easy cases cannot detect a regression on the hard 10%.

| Slice | Source signal | Why it earns space | Rough share |
|---|---|---|---|
| Typical traffic | Random within the head of the distribution | Guards against regressions on the common path | 40% |
| Explicit negative feedback | Thumbs-down, ratings | Known failures, already labelled by users | 15% |
| Implicit negative feedback | Regenerate, edit-after-copy, abandon | Far more plentiful than thumbs, nearly as informative | 10% |
| Human override / escalation | Support or review queue | The strongest signal you get — a human wrote the correction | 15% |
| Reliability failures | Schema errors, refusals, timeouts, retries | Cases that break the pipeline rather than the answer | 10% |
| Tail and adversarial | Longest, shortest, non-English, malformed, prompt-injection attempts | Where systems actually break | 10% |

```sql
-- candidate mining from a traces table
SELECT trace_id, input_text, output_text, feedback, tags
FROM llm_traces
WHERE feature = 'ticket_triage'
  AND ts > now() - interval '30 days'
  AND (feedback = 'down' OR regenerated OR human_override OR schema_failed)
ORDER BY random()
LIMIT 400;                       -- over-collect; labelling will reject many
```

Two constraints go on this from the start. Redact PII as you extract — an eval set is a long-lived artefact that ends up in a repo, in CI logs, and on laptops, so it must not be a copy of your production data. And record provenance on every case: which trace, which date, why it was selected. Six months later, "why is this the expected output?" is a question you will need to answer.

### 2. Label a Golden Set

**100–300 carefully reviewed cases beat 5,000 unreviewed ones.** The purpose is discriminating between two versions of a system, and a few hundred well-chosen cases do that reliably. Unreviewed bulk mostly adds runtime and false confidence.

```jsonl
{"id":"tri_042","tags":["ambiguous","bug-vs-feature"],
 "input":"The export button doesn't do what I expected.",
 "expected":{"category":"bug","urgency":"low"},
 "accept_also":[{"category":"feature_request","urgency":"low"}],
 "rubric":null,
 "provenance":{"trace":"7f2a9c","date":"2026-03-11","why":"human_override"},
 "split":"dev"}
```

Fields that repay the effort: `tags` (the only way to get an actionable breakdown later), `accept_also` (genuinely ambiguous cases should not be scored as failures), `provenance`, and `split`.

**Measure inter-annotator agreement on a sample.** Have two people independently label 50 cases and compute agreement. This is the most informative hour in the whole workflow:

| Agreement | Meaning | Action |
|---|---|---|
| > 90% | The task is well-specified | Proceed; one labeller for the rest |
| 70–90% | Normal for subjective tasks | Your ceiling is roughly the agreement rate — say so out loud |
| < 70% | **The spec is ambiguous, not the model** | Stop. Fix the definition before labelling more |

That last row is the finding teams most often skip past. If two competent humans cannot agree what the right answer is, no prompt will produce it consistently, and the eval score is measuring labeller noise. The fix is a written decision rule, not a better model.

**Split at labelling time, before anyone iterates.** Roughly 70% development, 30% held out. Prompt iteration overfits whatever set you read — after a dozen rounds the dev score has drifted several points above true performance, reliably, not occasionally. The held-out slice is checked only at ship decisions, and if you find yourself checking it weekly it has become a dev set and you need a new one.

Keep the case file in git, reviewed like code. A changed expected output is a change to the definition of correct and deserves the same scrutiny as a change to the prompt.

### 3. Pick the Cheapest Scorer That Discriminates

| Scorer | Right for | Cost | Latency | Failure mode |
|---|---|---|---|---|
| Exact / set match | Classification, routing, enum fields | Free | ms | Brittle on whitespace and case — normalise first |
| Field-level extraction match | Structured extraction | Free | ms | Partial credit needs designing |
| Schema validation | Any structured output | Free | ms | Valid is not correct |
| Deterministic assertions | "cites a real doc id", "no phone numbers", "≤ 200 chars", "never says X" | Free | ms | Underrated — write these first |
| Numeric tolerance | Amounts, dates, counts | Free | ms | Pick the tolerance deliberately |
| Embedding similarity | Paraphrase-tolerant prose matching | Cheap | ~10ms | Happily scores 0.85 for a subtly wrong answer |
| LLM judge, rubric-based | Open-ended prose, tone, helpfulness | $ | seconds | Needs its own validation; drifts with the judge model |
| Human review | Final arbiter, judge calibration | Expensive | days | Does not scale; reserve it |

Work down this list, not up. A "subjective" summarisation task usually decomposes into several free checks — did it stay under the length limit, did it mention the required entities, did it avoid fabricating a number not in the source, is every cited id real — plus one genuinely subjective residue. Those free checks run on every commit in under a second; the judge cannot.

**If you use an LLM judge, treat it as a model you are deploying.**

```python
JUDGE_RUBRIC = """Score the ANSWER against the REFERENCE for factual accuracy.

3 — Every claim is supported by the reference; no additions.
2 — Supported, but omits a materially important point.
1 — Contains a claim absent from the reference, or a minor contradiction.
0 — Contradicts the reference, or fabricates a specific fact, number, or citation.

Reply as JSON: {"reason": "<one sentence>", "score": <0-3>}
Give the reason first, then the score.
"""
```

Five rules make a judge usable:

1. **Concrete anchored levels.** "Rate helpfulness 1–10" produces noise; a four-level rubric with described boundaries produces something repeatable.
2. **Reason before score.** The ordering matters — a score emitted first is a guess the explanation is then written to justify.
3. **Pin the judge model and version it.** If the judge changes silently, your entire history of scores becomes incomparable. Record the judge model on every result.
4. **Validate against humans on ~50 cases.** Compute agreement. Below ~80% the judge is not fit to gate a deploy; fix the rubric and re-test. An unvalidated judge is an opinion generator that outputs a decimal point.
5. **Know its biases.** Judges favour longer answers, answers that echo the question's phrasing, and — when comparing — whichever candidate is presented first. Randomise position in pairwise comparisons, and keep length as a separate metric so you can see when a "quality win" was just verbosity.

### 4. Wire Into CI as a Gate

```yaml
# .github/workflows/llm-eval.yml
on:
  pull_request:
    paths: ["prompts/**", "src/llm/**", "evals/**", "config/models.yaml"]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run eval suite
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        run: |
          evals run \
            --set evals/dev.jsonl \
            --prompt-version "$(git rev-parse --short HEAD)" \
            --model-snapshot "$(yq .model config/models.yaml)" \
            --temperature 0 \
            --fail-under 0.82 \
            --fail-regression 0.03 \
            --baseline-from main \
            --report eval-report.json
      - name: Comment results on PR
        run: evals comment --report eval-report.json
```

**Two thresholds, because they catch different things.**

`--fail-under` is an absolute floor: never ship below the agreed quality bar. `--fail-regression` compares against the last green run on main and fails a drop larger than the threshold, *even if the result is still above the floor*. Without the second, a system at 0.91 degrades to 0.84 over five PRs and every one of them is green.

**Set the regression threshold above your noise floor.** Run the same configuration five times and measure the spread; if it varies by 2 points, a 1-point threshold will flap and the team will disable the gate within a fortnight. Reduce the noise first: pin the model snapshot, temperature 0 where the provider supports it, a fixed seed where offered, a frozen case file, and enough cases that a single flipped case does not move the score much (at n=50, one case is 2 points).

**What should trigger the gate:** prompt changes, model or snapshot changes, retrieval and chunking changes, tool definition changes, SDK and dependency bumps. Model upgrades especially — that is the gate's highest-value use, converting "the provider changed something" into a PR with a number attached.

**Report per tag, not just overall.** An aggregate is unactionable; the breakdown points at a specific problem.

```
LLM eval — dev set (n=210)                    PR #482 vs main@a1b2c3d
overall          0.847   (-0.011)   PASS
├─ typical       0.930   (+0.004)
├─ ambiguous     0.610   (-0.090)   ← regression concentrated here
├─ adversarial   0.950   ( 0.000)
├─ non_english   0.780   (+0.020)
└─ long_input    0.820   (-0.010)
schema_valid     1.000 | refusal_rate 0.014 | p95_latency 1.8s | cost/case $0.0031
```

Track cost and latency in the same report. A change that buys 2 points of quality for triple the cost is a tradeoff someone should make deliberately, and it is invisible if the harness reports quality alone.

Keep the runtime under about five minutes so the gate is part of the PR loop rather than a nightly surprise: parallelise the cases, cache results keyed by (case, prompt version, model), and keep the expensive judge scorers on a nightly full run if they are too slow for the PR path.

### 5. Track Drift Over Time

The same harness is your drift monitor, and this is its second-largest payoff. Run the full suite — dev and held-out — nightly against the production configuration, and store every result.

```python
record = {
    "ts": utcnow(), "suite_sha": sha_of("evals/"),
    "prompt_version": cfg.prompt_version,
    "model_requested": cfg.model, "model_resolved": resp.model,
    "overall": 0.847, "by_tag": {...},
    "cost_per_case": 0.0031, "p95_latency_ms": 1800,
}
```

Chart the score by date, sliced by `prompt_version` and `model_resolved`. Because the inputs are frozen, a step change cannot be traffic mix, seasonality, or a new customer cohort. It is either something you changed — visible in `prompt_version` — or something your provider changed, visible in `model_resolved` or in neither, which is itself informative.

This is also the only artefact that makes a vendor conversation productive. "Our users say it feels worse" gets sympathy; a dated, reproducible regression on a fixed input set, attributable to a model id change, gets an engineer.

**Keep the suite alive.** An eval set fixed at launch measures a product that no longer exists.

| Cadence | Action |
|---|---|
| Every incident | Add the failing case before fixing it — the regression test for LLM systems |
| Monthly | Mine new negative feedback; add 5–10 cases |
| Quarterly | Refresh ~20% from current traffic; retire cases everything passes trivially |
| On spec change | Re-review affected labels — the definition of correct moved |
| Never | Delete a hard case because it keeps failing |

Watch the ceiling too. When overall score approaches your measured inter-annotator agreement, the suite has stopped discriminating and further gains are noise. Either tighten the spec (raising the agreement ceiling) or add harder cases.

One discipline to hold: **do not tune directly against the held-out set.** The moment someone reads its failures and edits the prompt in response, it has become a second dev set and your honest estimate is gone. `prompt-iteration-cycle` covers the loop that runs against the dev set; this suite is what tells you whether that loop was actually making progress.

## Common Pitfalls

- **The prompt author writes the eval set, after the prompt.** The cases encode what the prompt already does, and the suite certifies the status quo forever.
- **Runs only on request.** It rots within a month; the number stops matching intuition; the team goes back to eyeballing.
- **One aggregate number.** Nothing is actionable — per-tag breakdown is where the diagnosis lives.
- **Judge deployed without validation.** You are gating deploys on an unmeasured model's opinion.
- **Judge model unpinned.** The scoring instrument changes under you and the whole history becomes incomparable.
- **Scoring not adjusted for judge bias.** Longer answers win; the first candidate wins; verbosity reads as quality.
- **No held-out split.** A dozen rounds of iteration inflate the dev score by several points, and it looks like progress.
- **Absolute floor only.** Gradual regression passes every PR and arrives as a step change in user complaints.
- **Regression threshold below the noise floor.** The gate flaps, and someone disables it.
- **Non-reproducible runs.** Floating aliases, non-zero temperature, an unversioned case file — the score becomes unfalsifiable.
- **Ambiguous cases scored as binary failures.** You penalise correct answers and chase phantom regressions.
- **Quality reported without cost and latency.** Expensive wins ship unnoticed.
- **Cases frozen at launch.** The suite measures a product that no longer exists.
- **Tuning against the held-out set.** The last honest number in the system is spent.

## Related Workflows

- [Prompt Iteration Cycle](../prompt-iteration-cycle) — the inner loop this harness scores
- [LLM Feature Build](../llm-feature-build) — where the first version of this eval set gets written
- [RAG Pipeline Setup](../rag-pipeline-setup) — retrieval-specific eval sets that plug into the same harness
