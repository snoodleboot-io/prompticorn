# User Testing Methods (Verbose)

## Core Patterns

### Choosing a Method

Start from the question, in writing, before choosing anything. Most wasted
research is a well-run study that structurally could not answer what was asked.

| Method | Typical n | Answers | Cannot answer | Cost |
|---|---|---|---|---|
| Moderated usability | 5–8 per segment | Where users get stuck and *why* | Rates, magnitudes | 1–2 days |
| Unmoderated usability | 15–30 | Same failures, more coverage, cheaper | The "why" behind an unexpected action | Hours |
| Guerrilla / hallway | 3–5 | Blatant confusion, fast | Anything domain-specific | Minutes |
| A/B test | 1,000s per arm | Which variant moves a metric | Why; anything with low traffic | 1–4 weeks |
| Multivariate test | 10,000s | Interactions between elements | Almost always underpowered in practice | Weeks |
| Diary study | 8–15, 2–4 weeks | Real context, frequency, triggers over time | Reactions to unshipped UI |  Weeks |
| Card sort (open) | 15–30 | Users' own grouping and vocabulary | Whether your existing IA works | Days |
| Tree test | 30–50 | Findability in a proposed IA | Visual design, page-level usability | Days |
| Five-second test | 20–50 | First impression, value-prop clarity | Task completion | Hours |
| Survey | 100s–1,000s | Distribution of *stated* attitudes | Behaviour, causes | Days |
| Session replay / funnel analytics | All traffic | Where drop-off happens, at what rate | Why they dropped | Ongoing |

The productive combination is nearly always a quantitative method that finds
*where* a problem is, followed by a qualitative one that explains *why*. Funnel
analytics says checkout step 3 loses 40%; six moderated sessions say people
cannot tell whether the discount was applied.

### Writing Usability Tasks

A task has a goal, a plausible motive, and an observable end state — and never
names the interface element under test.

❌ "Click the Settings icon, go to Team, and invite a new member."
✅ "A new designer starts Monday and needs access to your team's projects. Set
that up."
Success: an invitation is sent to an address they type.

❌ "Use the filter to find orders over $500."
✅ "Your manager wants to know which of last month's orders were unusually
large. Find them."
Success: a filtered or sorted view showing orders above a threshold.

❌ "Try out the new comparison feature and tell us what you think."
✅ "You're choosing between the Standard and Business plans for a team of 12.
Decide which one you'd buy and tell me why."
Success: a stated choice with a stated reason.

Checklist for every task:

- No product noun the user must locate ("export", "filter", "Settings")
- A realistic reason, not "we want to test X"
- Success criterion written down *before* the session
- One goal per task; if it needs an "and then", split it
- Where in the product it starts, stated explicitly

Randomise task order across participants where tasks are independent — otherwise
later tasks always benefit from familiarity acquired in earlier ones, and you
will mistake a learning effect for a design improvement.

### The Sample-Size Asymmetry

This is the single most misapplied idea in product research, so it is worth
being precise.

**Discovery (qualitative).** For a problem that affects a proportion *p* of
users, the chance of seeing it at least once in *n* sessions is `1 - (1-p)^n`.

| Problem affects | n=5 | n=8 | n=15 |
|---|---|---|---|
| 50% of users | 97% | 99.6% | ~100% |
| 30% of users | 83% | 94% | 99.5% |
| 10% of users | 41% | 57% | 79% |
| 5% of users | 23% | 34% | 54% |

That is where "five users find 85% of problems" comes from — it holds for
*common* problems, in *one* user segment, and it is a claim about detection, not
about frequency. Rare problems and additional segments both need more sessions.
Two distinct roles means 5+5, not 5.

**Measurement (quantitative).** Estimating a proportion is an entirely different
job. The 95% interval on a proportion is roughly `p ± 1.96·sqrt(p(1-p)/n)`.

| Observed | n | Approx. 95% CI |
|---|---|---|
| 2 of 5 fail (40%) | 5 | 7% – 81% |
| 20 of 50 fail (40%) | 50 | 27% – 55% |
| 160 of 400 fail (40%) | 400 | 35% – 45% |
| 1,600 of 4,000 (40%) | 4,000 | 38.5% – 41.5% |

Halving the margin of error costs four times the sample. This is why "60% of
users struggled with checkout (n=5)" is not a finding — the honest statement is
"three of five participants failed the checkout task; the true rate could
plausibly be anywhere from a fifth to four-fifths of users."

Report qualitative results as counts ("4 of 6 participants"), never percentages.
The percentage invents a precision the design cannot deliver.

### Sizing an A/B Test

Required sample per arm scales roughly with `1 / (minimum detectable effect)²`,
so halving the effect you want to detect quadruples the sample. At 80% power and
5% significance, two-sided, from a 5% baseline conversion:

| Target | Absolute lift | Per arm | Days @ 2,000/arm/day |
|---|---|---|---|
| 5.0% → 7.5% (+50%) | 2.5 pts | ~1,700 | 1 |
| 5.0% → 6.0% (+20%) | 1.0 pt | ~9,000 | 5 |
| 5.0% → 5.5% (+10%) | 0.5 pt | ~31,000 | 16 |
| 5.0% → 5.25% (+5%) | 0.25 pt | ~120,000 | 60 |

Three practical consequences:

1. **Run the calculation before building the variants.** If detecting a
   realistic effect takes eleven weeks, A/B testing is not the right tool for
   this decision. Ship on judgement, or test a bolder change.
2. **Big swings are cheap to test; polish is not.** Button-colour tests are
   almost always underpowered for the effect size they could plausibly produce.
3. **Round to whole weeks.** Tuesday traffic does not behave like Saturday
   traffic; a 5-day test partly measures the calendar.

Choose the minimum detectable effect from what would change your decision, not
from what you hope to see. If a 2% lift and a 0% lift would lead to the same
action, you do not need to distinguish them.

### Why Peeking Breaks Everything

A p-value assumes one analysis at a pre-specified sample size. Each additional
look is another opportunity for a random walk to wander across the threshold —
and random walks cross thresholds far more often than intuition suggests.

| Analyses during the test | Approx. actual false-positive rate |
|---|---|
| 1 (fixed n) | 5% |
| 5 | ~14% |
| 10 | ~19% |
| Continuous / daily over 2 weeks | 20–30% |

The behavioural version is worse than the statistical one: teams look daily,
stop when the result is favourable, and keep running when it is not. That
asymmetric stopping rule manufactures wins. It explains the common pattern where
a portfolio of "winning" tests never adds up to the growth the metric shows.

Three legitimate options:

```
Fixed-horizon:  compute n, run to n, analyse once. Simple, wasteful of time.
Sequential:     always-valid p-values / confidence sequences. Peek freely,
                pay a modest efficiency cost, keep the guarantee.
Group sequential: pre-specify k interim looks with an alpha-spending function
                (O'Brien-Fleming). Peek k times legitimately.
```

Monitoring for harm is different and always allowed: error rates, latency,
crashes, revenue collapse. That is a safety stop, not an efficacy decision, and
it does not touch your alpha for the primary metric.

### Running a Moderated Session

```
 2 min  Set expectations: "We're testing the design, not you.
        There are no wrong answers. Please think out loud."
 3 min  Warm-up: what they do, when they last did this task for real
25 min  3–5 tasks, one at a time, read aloud and also handed over in writing
 5 min  Retrospective: hardest part, what they expected, anything surprising
 2 min  Wrap, incentive, permission to follow up
```

Facilitator discipline, in order of importance:

1. **Silence.** After a pause, count to ten. Most insight arrives in second five.
2. **Deflect appeals.** "Is this right?" → "What would you expect to happen?"
3. **Never rescue.** Being stuck is the finding. Intervene only when the session
   cannot continue, and log the timestamp when you did.
4. **Never explain the interface.** If you have to explain it, you have found a
   defect, not a misunderstanding.
5. **Ask neutrally.** "What are you thinking?" not "was that confusing?"

Have the whole team watch live, not the highlight reel. A designer watching a
person fail is worth more than any report you could write about it.

### Analysing and Reporting

Rate severity so the readout is prioritisable rather than a wall of issues:

| Severity | Definition | Response |
|---|---|---|
| 1 – Blocker | Task cannot be completed, or data is lost | Fix before ship |
| 2 – Major | Completed only with significant struggle or a wrong turn | Fix this cycle |
| 3 – Minor | Completed; noticeable friction or hesitation | Backlog |
| 4 – Cosmetic | Noticed but did not impede | Opportunistic |

Report format: severity, the observed behaviour, count of participants affected
out of total, and a verbatim quote. "3 of 6 participants clicked 'Save' expecting
it to also publish; P4: 'so is it live now, or...?'" Do not report a fix as if it
were a finding — the finding is the behaviour; the fix is a separate decision
that belongs with `feature-planning`.

## Common Anti-Patterns

❌ **Choosing the method before writing the question** — the team likes usability
tests, so every question becomes a usability test.
✅ Write the question and what decision it unblocks, then pick from the table.

❌ **Percentages from tiny samples** — "60% failed (n=5)" implies precision that
is not there.
✅ Report counts: "3 of 5 participants failed."

❌ **A/B testing a low-traffic surface** — 200 visitors a week can never resolve
a 10% lift.
✅ Check the power calculation first; use qualitative methods where traffic is thin.

❌ **Stopping a test the day it turns significant** — inflates false positives to
20–30%.
✅ Fixed sample size analysed once, or a sequential method that permits peeking.

❌ **Tasks that name the target element** — "click Export" tests reading, not
findability.
✅ Give the goal and the motive; let them find the path.

❌ **The designer moderating their own work** — leading questions and rescues
follow, usually unconsciously.
✅ A neutral moderator; the designer observes silently.

❌ **Testing only with new users** — a change affecting daily power users is
evaluated by people who have never seen the product.
✅ Recruit for the segment the change actually targets; test both when muscle
memory is at risk.

❌ **Surveys asking about future behaviour** — "would you use this?" has the same
worthlessness in a survey as in an interview.
✅ Ask about last week's behaviour, or run a fake-door test.

❌ **Treating the A/B winner as an explanation** — the variant won; nobody knows
why, so the "learning" written down is fiction.
✅ Pair the test with sessions or session replay to explain the mechanism.

❌ **Running tests for 3 or 5 days** — day-of-week composition differs enough to
swamp small effects.
✅ Whole weeks, always.

❌ **No holdout, no re-test** — a suspiciously large win is never re-validated.
✅ Re-run surprising winners, or keep a small holdout for a cycle.

❌ **Research theatre** — a study run after the decision was made.
✅ Agree in advance what result would change the plan; if nothing would, skip it.

## User Testing Checklist

- [ ] The question and the decision it unblocks are written before method choice
- [ ] Method is capable of answering that question (checked against the table)
- [ ] Participants recruited from the segment the change affects
- [ ] Tasks state a goal and motive, and name no UI element
- [ ] Success criteria written down before the first session
- [ ] Task order randomised where tasks are independent
- [ ] Pilot session run and the guide fixed before real participants
- [ ] Moderator is not the person who designed the flow
- [ ] Team observes live sessions, not just the summary
- [ ] Qualitative results reported as counts, never percentages
- [ ] Findings severity-rated, with a verbatim quote each
- [ ] A/B tests have a pre-registered sample size and stopping rule
- [ ] Minimum detectable effect chosen from what changes the decision
- [ ] Tests run in whole weeks, with randomisation validated (A/A or SRM check)
- [ ] Analysis performed once, or by a sequential method that allows peeking
- [ ] Guardrail metrics monitored separately from the primary metric
- [ ] Surprising wins re-validated before being built on
