# Technical Decision Making (Minimal)

## Purpose
Spend analysis where it pays — heavily on decisions that are expensive to
reverse, barely at all on the ones you can undo next sprint.

## Core Techniques

### 1. Classify the Door Before You Analyse
A **two-way door** is cheap to walk back: a library choice behind an interface, a
cache layer, a CI runner, a feature flag rollout. A **one-way door** is expensive
or impossible to reverse: your primary datastore, a public API contract, a data
model that gets a year of writes, a vendor with your customer data.

| | Two-way door | One-way door |
|---|---|---|
| Analysis | Hours | Days to weeks |
| Who decides | The engineer doing the work | Team, with a written record |
| Evidence | A read of the docs | A spike, benchmark, or reference call |
| Output | A PR | An ADR (see `architecture-documentation`) |

Most conflict about process comes from applying one-way-door ceremony to
two-way-door decisions. The cost of that is not just meetings — it teaches the
team that decisions are heavy, so they stop making them.

### 2. Score With a Weighted Matrix, Then Argue About the Weights
Choosing a background job system for a Python API, 200 jobs/sec, existing
Postgres and Redis, 4-engineer team:

| Criterion | Weight | Celery+Redis | SQS+workers | Postgres queue |
|---|---|---|---|---|
| Ops burden (new infra) | 0.30 | 3 | 2 | 5 |
| Team familiarity | 0.25 | 5 | 2 | 4 |
| Delivery guarantees | 0.20 | 3 | 5 | 4 |
| Observability | 0.15 | 2 | 4 | 4 |
| Throughput headroom | 0.10 | 5 | 5 | 2 |
| **Weighted total** | | **3.55** | **3.10** | **4.15** |

Score 1–5 against a stated definition, not a vibe. The number is not the
decision — it is a way to surface that two people disagree about the *weights*
(is ops burden really 0.30?) rather than talking past each other about products.
If the top two are within ~0.3, the matrix says "these are equivalent, pick on
something else and move on".

### 3. Spike When the Deciding Fact Is Unknown
Do not spike to feel thorough. Spike when you can name the specific fact that
would change the answer, and only then. Write it as a question with a
time-box and a decision rule:

> "Can Postgres `SELECT ... FOR UPDATE SKIP LOCKED` sustain 200 jobs/sec on our
> db.r6g.large with the current write load? 2 days. If yes, Postgres queue. If
> it costs more than 15% of primary CPU, Celery."

If you cannot state what result would flip your choice, you are not gathering
evidence, you are procrastinating.

### 4. Record What Would Change Your Mind
Every non-trivial decision gets a falsifier written down at decision time:

> "Revisit if job volume exceeds 800/sec sustained, if we need cross-region
> workers, or if queue-wait p99 exceeds 5s for a week."

Written up front, this is honest engineering. Written later, it is always
motivated reasoning — you will find a reason the current choice is still fine.
It also ends the "we should never have done X" argument: either a trigger fired
or it didn't.

### 5. Disagree and Commit, Explicitly
When the team splits and the decision has an owner, the dissenter states their
objection once, in writing, and it goes in the record. Then everyone implements
the chosen option properly — no half-hearted build, no parallel prototype, no
relitigating in standup. The written objection is what makes this honest: if a
trigger fires later, the dissent is already on record and the revisit is fast.

Commitment does not mean silence forever. It means silence until new evidence.

## Warning Signs

- Weeks of analysis on something you could reverse in an afternoon
- A decision matrix built after the choice was made, with weights reverse-fitted
- Spikes with no stated question, time-box, or decision rule
- No named owner, so the decision quietly defaults to whoever writes code first
- Nobody can say what would make them change their mind
- The same choice re-argued monthly with no new information
- A dissenter who "committed" but is building a shadow alternative
- Reversible choices escalated to architecture review; irreversible ones made in a PR
