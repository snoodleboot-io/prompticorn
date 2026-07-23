# Success Metrics Definition (Verbose)

## Core Patterns

### The Metric Spec

A metric is not a name and a number. It is a specification precise enough that
two analysts who have never spoken produce the same value. Anything less
guarantees a reconciliation meeting.

```
Name:        week_1_activation_rate
Question:    Do new self-serve accounts reach the point where the product
             is doing real work for them, fast enough to survive week 2?
Definition:  Of accounts created in week W, the share that complete
             >= 3 project_created AND >= 1 teammate_invited within
             7 × 24h of accounts.created_at. Event timestamps, UTC.
Population:  signup_channel = 'self_serve'; excludes is_test = true and
             email domains in the internal-domains list.
Grain:       One row per signup cohort week.
Source:      warehouse.analytics.events (server-side), warehouse.core.accounts
Owner:       Priya Raman, PM Onboarding
Reviewer:    Analytics guild, quarterly definition audit
Baseline:    26.4% (2026-04-01 .. 2026-06-30, n = 11,840)
Target:      34% by 2026-12-31
Cadence:     Weekly in growth review; target revisited each quarter
Counter:     week_4_retention >= 61% (baseline 64%)
Version:     v2 (v1 counted 2 projects and no invite; changed 2026-05-04)
```

```sql
-- week_1_activation_rate v2
WITH cohort AS (
  SELECT id, created_at, date_trunc('week', created_at) AS cohort_week
  FROM core.accounts
  WHERE is_test = false
    AND signup_channel = 'self_serve'
    AND email_domain NOT IN (SELECT domain FROM core.internal_domains)
),
qualifying AS (
  SELECT c.id,
         count(*) FILTER (WHERE e.name = 'project_created')  AS projects,
         count(*) FILTER (WHERE e.name = 'teammate_invited') AS invites
  FROM cohort c
  JOIN analytics.events e
    ON e.account_id = c.id
   AND e.occurred_at >= c.created_at
   AND e.occurred_at <  c.created_at + interval '7 days'
  GROUP BY c.id
)
SELECT c.cohort_week,
       count(*)                                            AS signups,
       count(q.id) FILTER (WHERE q.projects >= 3
                             AND q.invites  >= 1)          AS activated,
       round(100.0 * count(q.id) FILTER (WHERE q.projects >= 3
                                           AND q.invites >= 1)
             / nullif(count(*), 0), 1)                     AS activation_pct
FROM cohort c
LEFT JOIN qualifying q ON q.id = c.id
WHERE c.cohort_week < date_trunc('week', now()) - interval '1 week'  -- exclude
GROUP BY 1 ORDER BY 1;                                    -- immature cohorts
```

Two details in that query do real work. `nullif(count(*), 0)` stops a zero-signup
week from erroring or silently returning null in a way people misread as zero.
The final `WHERE` excludes cohorts that have not yet had their full 7 days — the
single most common cause of a metric that "always dips at the end", which teams
then explain with elaborate stories about seasonality.

**Version, never redefine.** Changing v1 to v2 in place makes every historical
chart a lie: the step change in the graph is your definition, not user behavior.
Ship `week_1_activation_rate_v2` alongside v1, run both for a few weeks so the
offset is measurable, annotate the chart at the changeover date, then retire v1.

### Denominators Are Where Metrics Go Wrong

Every rate is a claim about a population. Leave the population implicit and the
metric becomes movable without touching the product.

| Metric as stated | Possible denominators | Spread on the same week |
|---|---|---|
| "Checkout conversion" | All sessions | 2.1% |
| | Sessions reaching /cart | 18.4% |
| | Sessions starting checkout | 61.2% |
| | Users who started checkout (dedup) | 68.9% |

All four are defensible; they answer different questions. The failure is quoting
one and having leadership hear another — 2.1% and 68.9% justify entirely
different investments.

Three rules that eliminate most of this:

1. **Put the denominator in the name.** `checkout_completed_per_checkout_started`
   is ugly and unambiguous. `conversion_rate` is neither.
2. **Publish the counts.** Never show `18.4%` alone; show `1,842 / 10,010`. A rate
   that improves while its denominator collapses is almost always a tracking
   regression, a filter change, or a bot filter that started working.
3. **Fix the population in the spec.** Bots, internal users, test accounts, and
   churned-then-returned users each shift rates by whole points.

A worked example of the trap:

```
Week 12:  1,100 / 10,000 = 11.0%
Week 13:    900 /  6,000 = 15.0%   "conversion up 4 points!"
```

Conversions fell by 200. A tracking script broke on mobile, the denominator lost
4,000 sessions, and the rate rose. This is why the counts are non-negotiable.
See `product-analytics-setup` for why client-side denominators drift.

### Leading and Lagging, and the Link Between Them

Lagging metrics are what the business is actually made of and are useless as
steering signals — by the time annual churn moves, the decisions that caused it
are four quarters old. Leading metrics move inside a sprint and are only worth
tracking if they genuinely predict the lagging one.

| Lagging (org owns) | Leading (team owns) | Hypothesised link | Lag |
|---|---|---|---|
| Gross revenue churn | Weekly active seats / licensed seats | Unused seats are not renewed | 2-4 mo |
| Net revenue retention | Seats added per account per month | Expansion precedes renewal uplift | 1-2 mo |
| Support cost per account | Week-1 ticket rate per new account | Confusion early creates load forever | 4-8 wk |
| Logo churn | Days since last admin login | Admin disengagement precedes cancellation | 1-3 mo |

The column that matters is "hypothesised link" — it is a claim, and claims get
tested. Write it down at the time you adopt the leading metric:

> "If weekly-active-seats/licensed-seats rises from 0.58 to 0.70, we expect gross
> churn to fall by at least 1.5 points within two quarters. If seat utilisation
> improves and churn does not move by 2027-Q1, the link is wrong and we replace
> this leading metric."

Without that, a team can hit its leading metric for a year while the business
degrades, and everybody's dashboard is green. The falsifier is the whole point;
the same discipline as recording what would change your mind about a technical
decision.

### Counter-Metrics and Guardrails

Any single metric under sustained pressure gets optimised in ways nobody
intended. This is not cynicism about people — it is what optimisation means. The
fix is structural: every goal metric ships with a guardrail that must hold.

| Goal | Degenerate strategy | Guardrail | Threshold |
|---|---|---|---|
| Activation rate | Remove the meaningful steps | week_4_retention | ≥ 61% |
| Trial→paid conversion | Aggressive interstitials | 30-day refund rate | ≤ 2% |
| Tickets closed/agent/day | Close without resolving | Reopen within 7d | ≤ 8% |
| Time in app | Confusing navigation | Top-3 task completion | ≥ 75% |
| Feature adoption | Modal that blocks the UI | Day-7 repeat use of feature | ≥ 40% |
| Email revenue | Increase send frequency | Unsubscribe per send | ≤ 0.3% |
| Model click-through | Recommend clickbait | Post-click dwell ≥ 30s | ≥ 55% |

The canonical case, with numbers:

```
Change: removed the "invite a teammate" requirement from onboarding.
  week_1_activation_rate   26.4%  ->  39.1%   (+12.7 pts)   goal metric ✓
  week_4_retention         64.0%  ->  51.3%   (−12.7 pts)   guardrail ✗
```

Activation did not improve; the bar moved. Because the guardrail was in the same
weekly review, this was caught in three weeks instead of surfacing as a churn
problem two quarters later, by which point the causal chain is unrecoverable.

Guardrails need pre-committed thresholds. A guardrail evaluated after the fact
always gets rationalised — "retention dipped, but that cohort was unusual."

### Frameworks, Only Once Made Concrete

HEART and AARRR are checklists for coverage, not metrics. They are worth using
exactly to the extent you fill them with specs like the one above.

HEART, instantiated for a collaborative document editor:

| Dimension | Signal | Metric | Target |
|---|---|---|---|
| Happiness | In-product survey after 5 sessions | CSAT mean, n ≥ 200/mo | ≥ 4.2/5 |
| Engagement | Real editing, not tab-open | Docs edited ≥ 2 min per WAU/wk | ≥ 3.5 |
| Adoption | New accounts reaching value | week_1_activation_rate | 34% |
| Retention | Account still working weekly | Week-4 account retention | ≥ 61% |
| Task success | Core flow completes | Share/permission flow completion | ≥ 92% |

AARRR for the same product needs its stage boundaries defined as events, or the
funnel is decorative: Acquisition = `signup_started`, Activation =
`week_1_activation_rate` as specified, Retention = week-4 active, Revenue = first
paid invoice, Referral = `teammate_invited` accepted within 14 days.

If you cannot write the query for a cell, the framework is not helping you yet.

## Common Anti-Patterns

❌ **"Improve activation"** as a goal — no definition, no baseline, no owner, so
success is decided by argument at quarter end.
✅ A named spec with a measured baseline, a numeric target, and one owner.

❌ **Redefining a metric in place** — historical charts become uninterpretable and
the step change gets attributed to product work.
✅ Version it (`_v2`), run both in parallel, annotate the changeover date.

❌ **Rates published without counts** — a broken tracker looks like a 4-point win.
✅ Always show numerator/denominator next to the percentage.

❌ **Goal metric with no guardrail** — the cheapest way to move a number is
usually to lower the bar it measures.
✅ Every target ships with a counter-metric and a pre-committed threshold.

❌ **Cumulative totals on dashboards** — "total users ever" only rises, so it can
never indicate a problem.
✅ Windowed, comparable metrics: weekly active, cohort retention.

❌ **Including immature cohorts** — the current partial week always looks like a
decline, and gets explained as a trend.
✅ Exclude cohorts that have not completed the measurement window.

❌ **Averages for latency, revenue, or session length** — long tails make the mean
describe nobody.
✅ Report p50 and p95, or a distribution. See `slo-sli-definition` for latency.

❌ **Metrics nobody reviews between goal-setting and quarter end** — an unwatched
metric cannot change a decision, which is the only reason to have it.
✅ A named cadence and a named person who presents it.

❌ **Team measured on a leading metric with an untested link** — green dashboard,
declining business.
✅ Write the predicted lagging effect and the date you check it.

## Success Metrics Checklist

- [ ] Every goal metric has a written spec with a precise definition
- [ ] Population filters stated: test accounts, internal users, bots, channel
- [ ] The measurement window and timezone are explicit
- [ ] Query committed to version control alongside the spec
- [ ] Baseline measured over a stated period before any target is set
- [ ] Target is a number with a date, not a direction
- [ ] Named single owner, plus a review cadence with a named forum
- [ ] Denominator named in the metric name; counts published with every rate
- [ ] Counter-metric defined with a pre-committed threshold
- [ ] Immature cohorts excluded from the current-period figure
- [ ] Metric versioned; definition changes ship as a new version with annotation
- [ ] Leading metrics carry a written, dated prediction about a lagging metric
- [ ] Every metric passes "if this doubled, what would we do differently?"
- [ ] Definitions audited quarterly against what the dashboards actually compute
