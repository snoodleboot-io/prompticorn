# Success Metrics Definition (Minimal)

## Purpose
Define metrics precisely enough that two people computing them independently get
the same number, and that moving one cannot quietly damage the business.

## Core Techniques

### 1. Write a Metric Spec, Not a Metric Name
"Activation rate" is not a metric. This is:

```
Name:       week_1_activation_rate
Definition: Of accounts created in week W, the share that complete
            >= 3 projects AND invite >= 1 teammate within 7 days
            of account_created (event timestamps, UTC).
Population: Self-serve signups only. Excludes accounts on
            @ourcompany.com domains and accounts flagged is_test.
Query:      see below
Owner:      Priya (PM, Onboarding)
Target:     34% by Q4 (baseline 26% measured 2026-04-01..06-30)
Cadence:    Reviewed weekly; target reset quarterly
Counter:    week_4_retention must not fall below 61%
```

```sql
SELECT date_trunc('week', a.created_at) AS cohort_week,
       count(*) AS signups,
       count(*) FILTER (WHERE act.activated) AS activated,
       round(100.0 * count(*) FILTER (WHERE act.activated)
             / nullif(count(*), 0), 1) AS pct
FROM accounts a
LEFT JOIN LATERAL (
  SELECT (count(*) FILTER (WHERE e.name = 'project_created')  >= 3
      AND count(*) FILTER (WHERE e.name = 'teammate_invited') >= 1) AS activated
  FROM events e
  WHERE e.account_id = a.id
    AND e.occurred_at < a.created_at + interval '7 days'
) act ON true
WHERE a.is_test = false AND a.signup_channel = 'self_serve'
GROUP BY 1 ORDER BY 1;
```

The spec is the artifact. Without the population filter and the window, three
dashboards will disagree by 8 points and you will spend a week reconciling them.

### 2. Always State the Denominator
A rate without a stated denominator is uninterpretable and usually gamed by
accident. "Conversion went from 4% to 6%" means nothing until you know whether
the denominator is all visitors, sessions, users who saw the pricing page, or
users who started checkout. Shrink the denominator and the rate rises with no
change to the business.

Name metrics so the denominator is in the name: `checkout_completion_per_started`
beats `conversion_rate`. Publish numerator and denominator counts alongside the
rate, always. A rate that jumps while the denominator collapses is a broken
pipeline or a filter change, not a win.

### 3. Pair Every Target With a Counter-Metric
Any metric under pressure will be optimized, including in ways you did not want.
The counter-metric is what makes the goal honest.

| Goal metric | Cheap way to move it | Counter-metric |
|---|---|---|
| Activation rate | Cut required steps to one trivial click | Week-4 retention ≥ 61% |
| Signups | Buy low-intent traffic | Paid-signup → activation ≥ 20% |
| Support tickets closed | Close without resolving | Reopen rate ≤ 8%, CSAT ≥ 4.2 |
| Session length | Slow, confusing navigation | Task completion rate ≥ 75% |
| Emails sent | Blast the whole list | Unsubscribe rate ≤ 0.3% |

The classic failure: activation climbs from 26% to 39% after the team removes the
teammate-invite step, and week-4 retention drops from 64% to 51%. Activation rose
because the bar was lowered. The counter-metric catches it in the same review.

### 4. Separate Leading From Lagging
Lagging metrics (revenue, net retention, annual churn) are why the business
cares but are useless for steering. Leading metrics move first and are what a
team can act on inside a sprint.

| Lagging | Leading | Typical lag |
|---|---|---|
| 12-month gross churn | Weekly active seats / licensed seats | 2-4 months |
| Expansion revenue | Seats added per account per month | 1-2 months |
| NPS | First-week support contact rate | 4-8 weeks |

Instrument the team on leading metrics, hold the org to lagging ones, and write
down the predicted link with a date to check it: "if seat utilisation rises from
0.58 to 0.70, gross churn falls ≥1.5pts by 2027-Q1." If it doesn't, the causal
story was wrong — replace the leading metric instead of defending it.

### 5. Reject Vanity Metrics With One Question
Ask: "if this number doubled next week, what would we do differently?" If there
is no answer, it is decoration.

| Vanity | Actionable replacement |
|---|---|
| Total registered users (cumulative, can only rise) | Weekly active accounts |
| Page views | Completion rate of the top 3 user tasks |
| Total events processed | p95 processing latency and failure rate |
| App downloads | Day-7 retained installs |

Cumulative counters are the strongest tell: they cannot go down, so they cannot
falsify anything.

## Warning Signs

- A metric named in a goal but with no written definition or owner
- Two dashboards reporting the same metric with different numbers
- Rates published without their numerator and denominator counts
- No counter-metric on any target
- A metric that improved right after its definition changed
- Cumulative "total ever" numbers on an exec dashboard
- Targets set with no baseline measured first
- Nobody has looked at the metric between the goal being set and the quarter ending
