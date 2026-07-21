# Team Collaboration (Minimal)

## Purpose
The mechanics that let several engineers change one codebase without blocking, duplicating, or silently diverging from each other.

## Core Techniques

### 1. Pick an Ownership Model Deliberately

| | Strong ownership | Collective ownership |
|---|---|---|
| Change quality | High in-area, gatekeeper knows the traps | Uneven, improves with tests |
| Bus factor | 1 — the failure mode | Spread |
| Cross-cutting change | Blocked on N owners' queues | Anyone can land it |
| Latency | Owner on leave = week-long stall | Any reviewer unblocks |

Default: **collective ownership with named stewards.** A steward is required for
review of their area but not required to write the change, and any change may be
made by anyone. This keeps the trap knowledge without making one calendar the
bottleneck. Escalation rule: if the steward has not responded in 24 hours, any
two other engineers may approve and merge.

### 2. Pair Only Where It Pays
Pairing costs 2 engineer-hours per hour. It earns that back when:
- The problem is novel and the design is still moving (two mental models beat one)
- Onboarding — a new hire's first change in an unfamiliar area
- A production incident, where a second pair of eyes prevents a second outage
- Debugging something that has already defeated one person for 3+ hours

It does not pay for routine CRUD, mechanical refactors, most bug fixes, or
anything one person already knows how to do. Mobbing (3+) is worth it for
exactly one thing: a decision everyone must live with, made once, together —
architecture selection, a naming convention, an incident postmortem.

### 3. Shape a Real First Week
```
Day 1  Laptop, access, and one merged PR — a typo fix counts. The
       point is proving the pipeline: clone → change → CI → deploy.
Day 2  Read-only tour with the steward: draw the request path for one
       real endpoint on a whiteboard. New hire draws it, not you.
Day 3  A real, small, scoped ticket. Pre-chosen before they started.
Day 4  Ship it. Pair on review, not on writing.
Day 5  Retro: what was confusing? Fix the docs — they are the only
       person who will ever see them fresh.
```
Assign one named onboarding buddy, not "ask anyone." "Ask anyone" means asking
no one.

### 4. Hand Off With State, Not Status
```
❌ "Handing off the billing migration, it's mostly done."

✅ Billing migration handoff → Marcus
   Branch: pro-455-billing-migration, 3 commits, CI green
   Done: schema + backfill script (dry-run verified on staging)
   Next step: enable the read path behind `billing_v2` flag
   Blocked on: finance approval for the 15-min write freeze
                (asked Oct 21, chase Dana)
   Trap: the backfill is NOT idempotent — re-running double-counts
         credits. Fix before any production run.
   Decisions made: chose per-account batching over global; see PRO-455.
```
The trap line is the reason handoffs exist.

### 5. Disagree in Writing Without Stalling
State your objection once, with its cost and your confidence. Then apply the
**two-round rule**: after two written exchanges without convergence, either
disagree-and-commit or escalate to a 15-minute synchronous call. Text is a poor
medium for an argument that has already failed once in text.

Say which you are doing: "I still prefer the queue, but I'm not confident enough
to block — going with your approach, and I'd revisit if we exceed 3k msg/s."

### 6. Make Time Zones a Design Constraint
With less than 3 hours of overlap, treat each handoff as a fixed cost of one day.
Sequential dependencies across zones are what kill velocity, not the zones
themselves. Split work so each zone owns a vertical slice end to end, and
protect the overlap window for things that genuinely need conversation.
Everything else is written and asynchronous.

## Warning Signs

- One person is the only reviewer for a directory
- "Ask anyone if you're stuck" is the onboarding plan
- A new hire's first PR lands after day 5
- Handoffs that say "mostly done" with no next step or known traps
- The same design argument recurring quarterly with no written record
- Pairing scheduled by policy rather than by problem
- An RFC open for 3 weeks with no decision deadline
- Standups where people report to a manager rather than unblock each other
