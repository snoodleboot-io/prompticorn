# Launch Readiness Checklist (Minimal)

## Purpose
Decide whether to ship using criteria agreed before anyone was emotionally
invested, and keep the ability to undo the decision cheaply.

## Core Techniques

### 1. Write Go/No-Go Criteria That Can Actually Fail
A criterion that cannot come back "no" is decoration. Each one needs a threshold,
a source, and a named owner who reports it.

| Gate | Criterion (fails if not met) | Source | Owner |
|---|---|---|---|
| Correctness | 0 open Sev-1/Sev-2 on the feature path | Issue tracker | QA lead |
| Performance | p95 < 400ms at 2× expected peak in load test | k6 run, dated | Backend |
| Observability | Dashboard live; alerts fire in staging test | Grafana + test alert | SRE |
| Rollback | Kill switch exercised in staging in the last 7 days | Runbook log | Backend |
| Support | Macros written; 6 agents trained; docs published | Support lead sign-off | Support |
| Legal/privacy | DPIA closed; new fields in the data map | Privacy review ticket | Legal |
| Capacity | Headroom ≥ 40% at projected peak; quotas raised | Capacity note | SRE |
| Comms | Changelog, in-app notice, and email scheduled | Marketing plan | PMM |

Compare with unfalsifiable versions: "testing complete", "performance acceptable",
"support is aware", "legal reviewed it". None of those can produce a "no", which
is why launches with green checklists still fail.

Record each answer as yes/no with a date and a person. "Mostly" is a no.

### 2. Rollback Before Rollout
You do not have a launch plan until you have rehearsed the undo. Before the
first user sees anything, confirm: the flag defaults off, killing it is one
action taking under 2 minutes, no deploy is required, and someone has actually
done it in staging this week.

Data is what makes rollback hard. Expand/contract migrations, dual-write with the
old path still readable, and no destructive schema change in the same release as
the feature. If a migration cannot be reversed, that is a written, accepted
decision with a forward-fix plan — not an oversight discovered at 2am. Details in
`deployment-rollback-strategies`.

### 3. Stage the Rollout With a Halt Metric per Stage
Every stage names its duration, its watch metrics, and the number that stops it.

| Stage | Audience | Duration | Halt if |
|---|---|---|---|
| 0 | Internal staff | 2 days | Any Sev-2, or 3+ staff bug reports |
| 1 | 1% of accounts | 24h | Error rate > 0.5%, or p95 > 600ms |
| 2 | 5% | 48h | Error rate > 0.3%, or activation down > 3pts vs control |
| 3 | 25% | 3 days | Any guardrail breach, or support tickets +20% |
| 4 | 100% | — | Flag stays in place for 2 weeks post-100% |

1% of a 200-account product is two accounts — statistically useless, so stage on
absolute exposure, not just percentage. And the halt condition must be a
pre-agreed number, because "error rate looks a bit high" at 25% always loses the
argument against shipping.

### 4. Run a Watch Window With Named Humans
The launch is not done at 100%; it is done when the watch window closes.

```
T+0 to T+4h    Author + on-call actively watching dashboards
T+4h to T+48h  On-call owns it; author reachable, escalation path published
T+48h to T+14d Daily metric check by the PM; flag remains removable
T+14d          Review: keep, iterate, or remove. Then delete the flag.
```

Publish the names and the escalation contact before launch. "The team will
monitor it" means nobody is watching. Never launch into a Friday afternoon or the
day before the owner's holiday.

### 5. Separate Technical Launch From Announced Launch
Ship the code dark, verify it in production with real traffic, then announce.
Coupling deploy and announcement means marketing timing dictates your rollback
decision, and you will be arguing about a press embargo while error rates climb.

Decouple: code deployed behind a flag on Monday, staged rollout Tuesday-Thursday,
announcement Monday the following week once the metrics have held.

## Warning Signs

- Criteria phrased so they can only be answered "yes"
- No rollback rehearsed, or rollback requires a deploy
- An irreversible migration shipping alongside the feature
- Rollout percentages with no halt metric attached
- Support and docs discovering the feature at launch
- The announcement scheduled before the rollout finishes
- Nobody named for the first four hours
- Launch on a Friday, or the owner unavailable in the watch window
