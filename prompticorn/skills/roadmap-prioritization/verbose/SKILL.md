# Roadmap Prioritization (Verbose)

## Core Patterns

### Capacity Is the Constraint, Not the Backlog

Prioritization arguments are usually capacity arguments in disguise. Start by
publishing the real number for the quarter:

```
Team: 5 engineers × 13 weeks         = 65 engineer-weeks
  − on-call rotation (1 eng/week)    = −13
  − support/escalation (~15%)        = −8
  − holiday, PTO, onboarding         = −9
  − keep-the-lights-on maintenance   = −10
  ------------------------------------------
  Available for planned roadmap work = 25 engineer-weeks
```

Twenty-five, not sixty-five. Most roadmap disappointment comes from planning
against the gross figure. Once the number is public, the conversation shifts from
"is this important?" (everything is) to "what fits in 25?" — which is answerable.

Allocate that capacity across buckets *before* scoring anything:

| Bucket | Allocation | Weeks | Rationale |
|---|---|---|---|
| Reliability / debt | 20% | 5 | Two Sev-2s last quarter traced to the job runner |
| Growth / retention | 50% | 12.5 | Core business, funds everything else |
| Strategic bets | 30% | 7.5 | Enterprise segment entry |

This allocation is the actual strategy. Any scoring model applied across the
whole backlog silently overrides it, because bets and paper cuts never score
comparably.

### RICE, Worked Through and Then Interrogated

RICE = (Reach × Impact × Confidence) / Effort.

- **Reach** — distinct users or accounts affected per quarter. Count, not
  guess: pull it from analytics, not from a feeling.
- **Impact** — per-user effect on the goal, on the fixed scale
  0.25 minimal / 0.5 low / 1 medium / 2 high / 3 massive.
- **Confidence** — 100% (data), 80% (some evidence), 50% (informed hunch).
  Below 50%, it is not an estimate; go get information instead.
- **Effort** — person-months, estimated by the people who will build it.

A real growth-bucket comparison:

| Item | Reach | Impact | Conf | Effort | RICE |
|---|---|---|---|---|---|
| Onboarding checklist redesign | 4000 | 1 | 80% | 1.5 | 2133 |
| Slack integration | 1800 | 2 | 80% | 2 | 1440 |
| Bulk import from CSV | 700 | 2 | 100% | 1 | 1400 |
| In-app search | 5200 | 0.5 | 80% | 2.5 | 832 |
| Dark mode | 9000 | 0.25 | 100% | 1 | 2250 |

Two useful readings. First, onboarding and dark mode are effectively tied (2133
vs 2250) — inside the noise of these inputs, so RICE is telling you it has no
opinion, and you should decide on strategy instead. Second, dark mode scoring
near the top should provoke suspicion, not a commitment. Its Impact of 0.25 is
multiplied by a huge Reach, which is how cosmetic work outranks substance.

**Where RICE breaks, concretely:**

| Failure | Mechanism | Mitigation |
|---|---|---|
| Starves big bets | Effort in the denominator penalises multi-quarter work linearly, while Confidence penalises novelty again | Bets get a protected allocation and are never RICE-ranked against paper cuts |
| Flatters cheap certainty | Confidence 100% only ever attaches to things you have already done before | Score bets within the bets bucket only |
| Reach dominates | Reach spans 3 orders of magnitude; Impact spans one (0.25–3) | Use log or banded reach, or cap the ratio |
| Invites gaming | Whoever wants their project funded adjusts Confidence from 50% to 80% | Estimates reviewed by someone with no stake in the outcome |
| Ignores timing | No term for deadlines or compounding cost | Use WSJF for anything time-sensitive |

RICE is a conversation forcing-function, not an oracle. Its value is that two
people disagreeing now have to say *which input* they disagree about.

### Cost of Delay and WSJF

Cost of Delay asks a different question: not "how much value?" but "how much
value per week of *not* doing it?" That is the right frame whenever value decays,
a deadline exists, or the cost of the work itself grows.

WSJF = Cost of Delay / Job Duration (duration in calendar weeks, not effort).

| Item | CoD components | CoD/wk | Dur | WSJF |
|---|---|---|---|---|
| PCI compliance for new processor | Hard deadline 30 Sep; missing it halts card payments | $60k | 8 | 7500 |
| SOC 2 automation | 3 enterprise deals blocked, ~$220k ARR | $18k | 6 | 3000 |
| Checkout latency (p95 4.1s → 1.5s) | ~0.8% conversion per 500ms on $2.4M/yr | $4k | 2 | 2000 |
| Admin UI refresh | Internal annoyance, no revenue link | $500 | 5 | 100 |

Three CoD shapes worth naming:

1. **Cliff** — value is constant then falls off a cliff (regulatory deadline,
   a conference date, a contract renewal). Schedule backwards from the cliff.
2. **Decay** — a competitor is shipping the same thing; value halves each
   quarter you wait.
3. **Compounding cost** — the job gets more expensive the longer you wait: a
   migration accumulating dual-write code, a backfill growing with the table.

Estimating CoD in dollars feels uncomfortable and is still better than not doing
it. A stakeholder who cannot put any number on the cost of waiting three months
has just told you it is not urgent.

### Commitment Requires Displacement

Treat the roadmap as a ledger where every entry balances.

❌ Not a commitment:

> "SSO is on the roadmap for Q3."

✅ A commitment:

> "SSO: 4 engineer-weeks, starts 14 Jul, target 8 Aug. Displaces the reporting
> rebuild, which moves to Q4. Owner: Priya. Agreed with Sales and with the
> reporting stakeholder, 12 Aug. Risk: SAML testing with the customer IdP may add
> a week."

Keep a visible change log:

| Date | Added | Removed | Requested by | Approved by |
|---|---|---|---|---|
| 12 Aug | SSO/SAML (4w) | Reporting rebuild (9w) | Sales (Dana) | Head of Product |
| 03 Sep | Partner dashboard (5w) | Billing retries (5w) | CEO | Head of Product |

This log answers "why did we ship so little this quarter?" with facts. It also
makes a pattern visible that no individual decision reveals: if the log shows six
swaps in a quarter, the problem is not prioritization, it is that the planning
horizon is longer than the organisation's attention span. Shorten the horizon.

### The Executive Escalation

Escalations are information — an exec often knows about a renewal or a board
commitment you don't. The failure is not that the queue gets jumped; it is that
it gets jumped invisibly, and the displaced work quietly dies.

A working response has four parts: acknowledge, price, name the displacement,
request the decision.

> "Understood — the partner dashboard for the Acme launch.
> It's about 5 weeks including the permissions work.
> Starting it Monday means billing retries don't ship this quarter; those recover
> roughly $30k/mo in failed charges, so the swap costs ~$90k over the quarter
> against the Acme relationship.
> If that's the right trade, say so and I'll move it today and tell the team."

Note what is absent: no arguing about whether the request is good, no silent
absorption "somehow", no passive-aggressive escalation to their manager. The
decision is theirs; the trade-off is yours to make legible. If the answer is "do
both", the honest reply is that both slip, and by how much.

If escalations arrive weekly, the roadmap is not the problem. Fix the intake:
one queue, one owner, a standing 30-minute weekly slot where swaps are decided.

### Saying No

Most "no"s fail because they are opinions, and opinions invite rebuttal. Anchor
on capacity and on criteria instead.

| Situation | Weak no | Working no |
|---|---|---|
| Low-value request | "That's not a priority." | "It's ~6 weeks. Ahead of it are SSO and the checkout fix. Which slips?" |
| Recurring pet feature | "We've discussed this." | "We'll build it when 5+ paying accounts ask unprompted, or one deal names it as blocking. We're at 2." |
| Vague strategic ask | "Can you write a doc?" | "What decision does it change? If we shipped it and nothing moved, what would we have expected to move?" |
| Genuinely good, wrong time | "Maybe later." | "Yes, but Q1 not Q3 — it depends on the billing refactor. Here's the sequence." |

The criterion version is the strongest form: it converts a rejection into a
condition the requester can go satisfy, which is both more respectful and more
likely to produce evidence. Record the criterion so you are held to it.

Decisions and their reversal triggers are worth writing down in the same style
described in `technical-decision-making` — the falsifier at decision time, not
reconstructed afterwards.

## Common Anti-Patterns

❌ **One global RICE-sorted list** — bets and paper cuts on one ranking. Cheap
certain work wins forever and the strategy never gets funded.
✅ Allocate capacity to buckets first; rank only within a bucket.

❌ **Effort estimated by the requester or the PM** — consistently 2–3× optimistic
on exactly the items they most want built.
✅ Effort comes from the engineers who will do the work, after a short look.

❌ **Confidence 80% on every row** — a constant multiplier changes no ranking and
launders guesses as analysis.
✅ Reserve 100% for measured evidence, 50% for hunches, and make people justify it.

❌ **Adding to the quarter without removing** — commitments become aspirations and
the team learns the roadmap is fiction.
✅ Every addition names its displacement, in writing, with an approver.

❌ **Absorbing escalations silently** — the exec never learns their request cost
$90k of billing work, so they keep escalating.
✅ Price the swap out loud and make them decide.

❌ **Roadmaps as dated feature lists 12 months out** — precision the evidence
cannot support, and every date becomes a broken promise.
✅ Now / Next / Later, with dates only on the current quarter's committed items.

❌ **No record of what was declined** — the same request returns every six weeks
and is re-argued from zero.
✅ A decisions log with the criterion that would change the answer.

❌ **"We'll do both"** — capacity is unchanged, so both slip and quality drops.
✅ State the new dates for both and let the stakeholder react to real numbers.

## Roadmap Prioritization Checklist

- [ ] Quarterly capacity published net of on-call, support, PTO, maintenance
- [ ] Capacity allocated across maintenance / growth / bets before scoring
- [ ] Each item scored within its bucket only, not across buckets
- [ ] Reach numbers pulled from analytics, not estimated
- [ ] Effort estimated by the implementing engineers
- [ ] Confidence below 50% sent back for evidence rather than scored
- [ ] Time-sensitive items scored with CoD/WSJF, not RICE
- [ ] Every committed item has an owner, a start date, and a target date
- [ ] Every addition to a committed quarter names what it displaced
- [ ] Swap log maintained with requester, approver, and date
- [ ] Declined items recorded with the criterion that would revive them
- [ ] Committed weeks sum to less than available weeks
- [ ] Dates published only for the current quarter; later horizons undated
- [ ] Roadmap reviewed on a fixed cadence, not renegotiated ad hoc
