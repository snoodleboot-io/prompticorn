# Roadmap Prioritization (Minimal)

## Purpose
Turn a list of things everyone wants into an ordered sequence you can defend,
and make the cost of every "yes" visible as a specific "no".

## Core Techniques

### 1. Score With RICE, Then Read the Failure Mode
RICE = (Reach × Impact × Confidence) / Effort. Reach is users touched per
quarter, Impact is 0.25/0.5/1/2/3 (minimal→massive), Confidence 50/80/100%,
Effort in person-months.

| Item | Reach | Impact | Conf | Effort | RICE |
|---|---|---|---|---|---|
| Fix CSV export encoding bug | 900 | 1 | 100% | 0.25 | 3600 |
| Copy tweak on signup form | 12000 | 0.25 | 100% | 0.1 | 30000 |
| SSO / SAML for enterprise | 40 | 3 | 80% | 4 | 24 |
| Rebuild reporting on a new store | 6000 | 2 | 50% | 9 | 667 |

The copy tweak outscores SSO by more than 1000×. That is RICE working exactly as
designed and being wrong. It multiplies certainty into the numerator and divides
by effort, so it systematically flatters small, cheap, certain wins and starves
anything big, slow, or uncertain — which is every strategic bet you have. SSO
reaches 40 accounts, but they are the six-figure contracts that unblock a segment.

Use RICE to rank *within* a bucket, never across buckets. Split the roadmap into
maintenance / growth / bets, allocate capacity first (say 20/50/30), then let
RICE order each bucket. The allocation is the strategy; RICE is only the sorting.

### 2. Use Cost of Delay When Timing Is the Whole Argument
WSJF = Cost of Delay / Job Duration, where CoD is value lost per week of waiting.

| Item | CoD/week | Duration (wk) | WSJF |
|---|---|---|---|
| SOC 2 evidence automation (blocks 3 deals) | $18k | 6 | 3000 |
| Checkout latency work | $4k | 2 | 2000 |
| Admin UI refresh | $500 | 5 | 100 |

CoD captures what RICE cannot: deadlines, expiring opportunities, and costs that
compound. A migration whose CoD climbs every week — dual-write overhead, a
growing backfill — should be scheduled before its CoD outruns the team.

### 3. "Q3" Is Not a Commitment Unless Something Left
Adding work to a full quarter without removing work is not planning, it is
wishing. The only honest form of a commitment is paired:

> "Yes to SSO in Q3. The reporting rebuild moves to Q4. Confirmed with the
> reporting stakeholder on 12 Aug."

Publish capacity as a number — 18 engineer-weeks after on-call, support rotation
and holiday — and require the committed items to sum to less than it. A roadmap
that never displaces anything carries no information.

### 4. Handle the Escalation as an Exchange, Not a Veto
An exec asking for something to jump the queue is legitimate; they may hold
information you don't. What is not legitimate is jumping without cost. Answer
with the swap rather than with resistance:

> "We can start the partner dashboard Monday. It's 5 weeks, which pushes
> billing-retry work out of the quarter. Billing retries recover about $30k/mo in
> failed charges. Confirm the swap and I'll update the roadmap today."

Then log it: what came in, what went out, who decided, when. Three months later
that log is the only thing that explains the quarter's output.

### 5. Say No in Trade-off Language
A "no" that references capacity survives; a "no" that references opinion gets
relitigated. Hand the requester the lever:

> "Not this quarter. It's ~6 weeks and the queue ahead of it is SSO and the
> checkout latency fix. If it should go first, tell me which of those slips."

Then give a real answer to "what would change this" — a revenue threshold, a
support ticket volume, a named customer count. That makes it a criterion rather
than a brush-off, and it ends the negotiation cleanly either way.

## Warning Signs

- Every item is P0, or priority tracks whoever asked most recently
- RICE scores compared across a bug fix and a platform bet as if commensurable
- Effort estimates supplied by someone who will not do the work
- Confidence set to 80% on everything by default, so the term cancels out
- New commitments added mid-quarter with nothing removed
- No written record of who approved which swap
- Nobody can name something the team decided not to do this quarter
- More items in flight than the team has people
