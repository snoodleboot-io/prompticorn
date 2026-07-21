# Launch Readiness Checklist (Verbose)

## Core Patterns

### Falsifiable Go/No-Go Criteria

The purpose of a readiness review is to produce a decision that could have gone
the other way. Most reviews cannot: the criteria are phrased so that "yes" is the
only grammatically available answer, and the meeting becomes a ritual performed
on the way to a launch that was never in question.

The test for a criterion is simple — can you describe the state of the world in
which it returns "no"? If not, rewrite it.

| Unfalsifiable | Falsifiable replacement |
|---|---|
| "Testing is complete" | "0 open Sev-1/Sev-2 on the feature path; regression suite green on the release SHA" |
| "Performance is acceptable" | "p95 < 400ms and p99 < 1.2s at 2× projected peak in a load test run against the release build within 7 days" |
| "We have monitoring" | "Dashboard published at <url>; a synthetic failure in staging fired the page to the on-call rotation on <date>" |
| "We can roll back" | "Kill switch exercised in staging on <date> by <name>; measured time-to-disable 45s; no deploy required" |
| "Support is aware" | "6 agents trained; 4 macros published; help article live; support lead signed off on <date>" |
| "Legal reviewed it" | "DPIA closed <ticket>; 3 new personal-data fields added to the data map; retention set to 24 months" |
| "We have capacity" | "40% headroom at projected peak; Stripe and SendGrid quotas raised; DB connection pool sized for +30% connections" |

Record each as an explicit yes/no with a date and a person. Ambiguous answers —
"mostly", "should be fine", "we'll finish it during rollout" — count as no. That
rule has to be stated in advance, because in the room, under launch pressure,
"mostly" reliably converts to yes.

Give one person the authority to call no-go, and make it someone whose incentives
are not tied to the launch date. If only the feature owner can stop the launch,
the gate does not exist.

### The Six Readiness Domains

Coverage matters as much as rigour. Launches rarely fail on the thing the team
was staring at; they fail on the domain nobody owned.

**1. Observability** — you cannot make a rollout decision on data you don't have.

| Item | Gate | Owner |
|---|---|---|
| Feature dashboard | Published, linked in the runbook | SRE |
| Error rate by endpoint | Baseline recorded pre-launch | Backend |
| Latency p50/p95/p99 | Baseline recorded pre-launch | Backend |
| Business metric | Activation/conversion split by flag state | PM |
| Alerts | Fired end-to-end in staging, reached the pager | SRE |
| Logs | Feature path emits correlation ids; sampling verified | Backend |

The pre-launch baseline is the item most often skipped and most often needed. At
stage 2 someone will ask "is a 0.4% error rate normal for this endpoint?" and
without a recorded baseline the answer is a guess. Alert thresholds should follow
`slo-sli-definition` rather than being invented for the launch.

**2. Rollback** — see `deployment-rollback-strategies` for mechanics; the launch
gate is that it has been *exercised*, not that it exists.

| Item | Gate |
|---|---|
| Flag default | Off in production before rollout begins |
| Disable path | Single action, < 2 min, no deploy, documented in the runbook |
| Rehearsal | Performed in staging within the last 7 days, by name and date |
| Data reversibility | Expand/contract; no destructive change in this release |
| Dual-write | Old read path still functional for the rollback window |
| Irreversible steps | Listed explicitly, with a forward-fix plan and an approver |

The last row is the one that saves launches. Almost every launch contains
something that cannot be undone — an email sent, a webhook delivered, a partner
notified, a backfill applied. Enumerating them beforehand turns "we can roll
back" from a comforting belief into an accurate, bounded statement.

**3. Support and documentation** — the cost lands here first.

| Item | Gate |
|---|---|
| Help article | Published and reachable from the feature |
| Support macros | Written for the top 3 predicted questions |
| Agent training | Session held; ≥ 80% of the rotation attended |
| Escalation path | Named engineer and channel for the watch window |
| Known limitations | Written down, shared with support before stage 1 |
| Ticket tagging | Tag created so launch-driven volume is measurable |

That last item is quietly important: without a tag, "did support volume go up?"
becomes unanswerable, and it is one of the halt signals.

**4. Legal, privacy, security**

| Item | Gate |
|---|---|
| New personal data | Added to the data map with a lawful basis and retention |
| DPIA | Completed where new categories or processing are introduced |
| Sub-processors | Any new vendor added to the public list, notice period observed |
| Terms / policy | Updated if behaviour or data use changes |
| Deletion | Feature's data covered by the existing DSR deletion path |
| Security review | Threat model reviewed; findings closed or accepted in writing |
| Accessibility | Keyboard path and screen reader verified on the core flow |

Sub-processor notice periods are a common trap — many contracts require 30 days'
notice, which is a calendar constraint no amount of engineering can compress.

**5. Capacity**

| Item | Gate |
|---|---|
| Load test | 2× projected peak against the release build, within 7 days |
| Headroom | ≥ 40% at projected peak on CPU, memory, connections |
| Database | Query plans reviewed; new indexes live and analysed |
| Third-party quotas | Raised in advance, with the ceiling documented |
| Cost | Projected infrastructure delta estimated and approved |
| Rate limits | Feature endpoints protected against pathological use |

Estimate peak from a real distribution, not the mean. If 60% of activity lands in
a 3-hour window, peak is roughly 5× the hourly average — and load-testing against
the average is how launches fail at 09:00 on the first business day.

**6. Communications**

| Item | Gate |
|---|---|
| Internal announcement | Sent before external, so nobody hears it from a customer |
| Changelog | Written, scheduled |
| In-app notice | Targeted at the rolled-out cohort only |
| Sales/CS enablement | Briefed; knows who is in each rollout stage |
| External timing | Scheduled *after* the rollout reaches 100% and holds |

Targeting matters: announcing to 100% of users a feature that 5% can see
generates support volume from people who cannot find it, which corrupts exactly
the ticket signal you are using as a halt condition.

### Staged Rollout With Halt Conditions

Stages are only useful if each one has a defined duration, a watch set, and a
pre-agreed number that stops it. Without the number, every borderline signal
resolves in favour of continuing, because the team wants to be finished.

| Stage | Audience | Min duration | Watch | Halt if |
|---|---|---|---|---|
| 0 dogfood | Internal staff (~120) | 2 days | Bug reports, error logs | Any Sev-2, or ≥ 3 distinct staff reports |
| 1 canary | 1% accounts, min 50 | 24h | Error rate, p95, logs | Errors > 0.5%, or p95 > 600ms, or any Sev-2 |
| 2 early | 5%, min 250 | 48h | + activation, support tags | Errors > 0.3%, p95 > 500ms, activation −3pts vs control, tickets +20% |
| 3 majority | 25% | 3 days | + retention, revenue path | Any guardrail breach, or revenue-path errors > 0.1% |
| 4 full | 100% | — | Full watch window | Flag retained and removable for 14 days |

Practical constraints that get missed:

- **Percentages are meaningless at low volume.** 1% of 200 accounts is 2 accounts;
  no error rate is measurable there. Set stages on absolute exposure with a
  minimum count, as above.
- **Randomise by account, not by request.** Per-request assignment gives a single
  user an inconsistent product and makes every bug report irreproducible.
- **Hold each stage for at least one full business cycle.** A stage that runs
  overnight has not seen a weekday morning peak.
- **Halt means halt, not "watch more closely."** Define the action too: flag off,
  then investigate. Cheap to redo, expensive to have skipped.
- **Keep a control group** through stage 3 if you intend to make any claim about
  the feature's effect. Without it, seasonality is indistinguishable from impact.

### The Watch Window

A launch is not complete at 100%; it is complete when the watch window closes with
someone's signature on it.

```
T+0 → T+4h      Author + on-call actively watching. Dashboards open.
                Explicit check-in at T+1h and T+4h in the launch channel.
T+4h → T+48h    On-call owns it. Author reachable, contact published.
                Support flags launch-tagged tickets to the channel.
T+48h → T+14d   PM checks the metric set daily. Flag stays removable.
T+14d           Written review: keep / iterate / remove. Flag deleted if kept.
```

Publish the names and phone-reachable contacts before the rollout starts. "The
team will keep an eye on it" is the state in which nobody is watching, and it is
the default outcome of not writing names down.

Timing rules worth treating as hard: no launch after Thursday midday, none the
day before the owner's holiday, none during a change freeze, and none within 48
hours of a dependent third-party's own maintenance window. These are not
superstition — they are about whether a competent human is available in the four
hours when it matters.

Set a stale-flag date at launch time. Flags left permanently produce a
combinatorial mess of code paths that nobody has tested together; the 14-day
review is where the flag is deleted, and it belongs in the sprint.

## Common Anti-Patterns

❌ **Criteria phrased so "no" is impossible** — "testing complete", "perf fine".
The review becomes theatre.
✅ Thresholds with a number, a source, an owner, and a date.

❌ **Rollback documented but never rehearsed** — the runbook references a flag
renamed two sprints ago, discovered at 02:00.
✅ Exercise the kill switch in staging within 7 days of launch; record who and when.

❌ **Destructive migration in the launch release** — column dropped, so rollback
means restoring from backup.
✅ Expand/contract; destructive steps ship at least one release later.

❌ **Rollout percentages with no halt metric** — every stage advances because
nothing was defined as bad enough to stop.
✅ Pre-agreed numeric halt condition per stage, with the halting action named.

❌ **Announcing before the rollout completes** — marketing timing now overrides
your rollback decision.
✅ Ship dark, verify in production, announce after 100% holds.

❌ **Support learning about it at launch** — first-day volume with no macros, no
docs, no escalation path.
✅ Support and docs are launch gates, complete before stage 1.

❌ **"The team will monitor"** — no name, so no one.
✅ Named humans per watch phase with reachable contacts, published in advance.

❌ **Friday launches** — the watch window falls on a weekend with a skeleton crew.
✅ Launch Monday to Thursday morning.

❌ **No pre-launch baseline** — no way to tell whether the current error rate is
elevated.
✅ Record baseline error, latency, and business metrics before stage 1.

❌ **No control group** — every post-launch movement is attributed to the feature,
including seasonality.
✅ Hold back a control cohort through stage 3.

❌ **Flag never removed** — permanent branching that nobody tests together.
✅ A dated removal ticket created at launch, closed within 14 days of 100%.

## Launch Readiness Checklist

**Go/no-go process**
- [ ] Every criterion has a number, a source, an owner, and a date
- [ ] A single named person holds authority to call no-go
- [ ] "Mostly" counts as no, stated in advance
- [ ] Decisions recorded as yes/no with names and timestamps

**Observability**
- [ ] Feature dashboard published and linked from the runbook
- [ ] Baseline error rate, latency, and business metrics recorded pre-launch
- [ ] Alerts exercised end-to-end in staging and reached the pager
- [ ] Metrics can be split by flag state, with a control cohort

**Rollback**
- [ ] Flag defaults off in production
- [ ] Disable is a single action, under 2 minutes, no deploy
- [ ] Kill switch exercised in staging within the last 7 days, by name
- [ ] Migrations follow expand/contract; nothing destructive this release
- [ ] Irreversible side effects enumerated with a forward-fix plan

**Support and docs**
- [ ] Help article published and linked from the feature
- [ ] Macros written for the top 3 predicted questions
- [ ] Agents trained; support lead signed off
- [ ] Escalation contact published for the watch window
- [ ] Ticket tag created so launch volume is measurable

**Legal, privacy, security**
- [ ] New personal data in the data map with basis and retention
- [ ] DPIA completed where required
- [ ] Sub-processor list updated, notice period observed
- [ ] Feature data covered by the deletion path
- [ ] Security findings closed or accepted in writing
- [ ] Keyboard and screen reader paths verified

**Capacity**
- [ ] Load test at 2× projected peak against the release build
- [ ] ≥ 40% headroom at peak on CPU, memory, connections
- [ ] Query plans reviewed; new indexes live
- [ ] Third-party quotas raised in advance
- [ ] Cost delta estimated and approved

**Rollout and watch**
- [ ] Stages defined with audience, minimum count, duration, halt condition
- [ ] Assignment randomised by account, not by request
- [ ] Named owner per watch phase with reachable contact
- [ ] Launch window is Monday–Thursday morning, outside any freeze
- [ ] Announcement scheduled after 100% and after the metrics hold
- [ ] T+14d review scheduled; flag removal ticket created at launch
