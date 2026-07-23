# Technical Debt Management (Minimal)

## Purpose
Treat debt as a portfolio with measurable carrying costs, so paydown competes for
budget on evidence instead of on how strongly an engineer sighs about it.

## Core Techniques

### 1. Write Register Entries With Principal and Interest
A debt item nobody can price will never be scheduled. Every entry names four
things: what and where, the interest (cost per change, recurring), the principal
(one-off cost to fix), and the trigger that makes paydown due.

> **DEBT-114 — Order totals recomputed in three places**
> **Where:** `checkout/pricing.py`, `admin/order_edit.py`, `jobs/reconcile.py`
> **Interest:** every pricing rule change costs ~3 engineer-days instead of ~1,
> because all three paths need editing and reconciling. 6 pricing changes in the
> last year → **~12 engineer-days/year**, plus 2 of the last 5 sev-2 billing
> incidents traced to divergence between them.
> **Principal:** ~8 engineer-days to extract one `PricingEngine` and migrate all
> three call sites, behind a shadow-compare in production for two weeks.
> **Trigger:** the multi-currency work in Q3 touches pricing — pay it down first,
> or pay ~3× on every ticket in that epic.
> **If not paid:** interest rises; multi-currency adds a fourth call site.

Payback here is under a year, which is what makes it a decision rather than a
complaint. Estimate interest from real history — commits touching the area, cycle
time on tickets in it, incidents attributed to it — not from intuition.

### 2. Classify With Fowler's Quadrant
| | Deliberate | Inadvertent |
|---|---|---|
| **Prudent** | "Ship the hardcoded tax table to hit the launch; replace after" | "Now we understand the domain, the aggregate boundary is wrong" |
| **Reckless** | "No time for tests, just merge it" | "What's a repository pattern?" |

The quadrant is not a scoring exercise; each cell gets a different response.
Prudent-deliberate needs a register entry and a trigger at the moment of the
decision. Prudent-inadvertent is learning — refactor when the next change makes
it cheap. Reckless-deliberate is a process failure: fix the pressure that caused
it, because it will recur. Reckless-inadvertent is a capability gap, addressed by
review and pairing, not by a refactor ticket.

### 3. Fund Paydown With a Budget, Not Good Intentions
The boy-scout rule ("leave it cleaner") cannot repay structural debt. Nobody
extracts a service or splits a 4,000-line module opportunistically while fixing a
bug, and reviewers rightly resist unrelated changes in a bugfix PR. It handles
lint-level debt only.

What works is an explicit, defended allocation — typically 15–20% of sprint
capacity — with paydown items on the same board and estimated the same way as
features. Non-negotiable rules: the allocation is protected during crunch (crunch
is caused by debt), each item ships with a measurement of the interest it
removed, and it is never the last item in the sprint, because the last item is
what gets dropped.

### 4. Do Not Pay Down Debt That Is About to Die
Refactoring is an investment that only returns through future changes to that
code. Skip it when:

- The module is scheduled for deletion or replacement within two quarters.
- It is stable and untouched — one commit in three years, no incidents. Ugly and
  quiet is not debt; it charges no interest.
- The fix costs more than the remaining lifetime interest.
- Payback exceeds the code's expected life. A 20-day refactor saving 2 days/year
  on a system with 3 years left is a loss.

Change frequency is the sharpest filter. Debt in a file touched weekly is
expensive; identical debt in a file touched annually is nearly free. Rank by
`interest × change frequency`, not by how bad the code looks.

### 5. Translate to Money and Risk for Funders
Executives do not fund "the auth module is a mess". They fund outcomes in their
own units:

| Engineering framing | Funder framing |
|---|---|
| Duplicated pricing logic | ~12 engineer-days/year of rework; 2 of 5 recent billing incidents |
| No integration tests on checkout | Change failure rate 28% on checkout vs 9% elsewhere |
| Manual release process | 6 hours of engineer time per release, 40 releases/year |
| Framework three majors behind | 14 unpatched CVEs; upgrade cost doubles roughly each major |

Say it as: "This costs us X per quarter and rises. It costs Y once to stop. It
pays back in Z months." That is a capital-allocation question they already know
how to answer. Debt with a compounding rate — dependency drift, migrations that
get harder with data volume — should be shown with its growth curve.

## Warning Signs

- A debt backlog with no estimates, no interest figures, and no triggers
- Paydown that only ever happens in slack time, which never arrives
- The refactor allocation being the first thing cut when a date slips
- "We'll clean it up after launch" with no ticket and no trigger
- Big-bang rewrites proposed instead of incremental, measurable paydown
- Refactoring the ugliest code rather than the most frequently changed code
- Debt argued on aesthetics, with no cost-per-change anyone can name
- Reckless debt recurring while the schedule pressure that caused it is untouched
- Nobody can name a single item paid down last quarter or what it saved
