# Stakeholder Communication (Minimal)

## Purpose
Keep the people who depend on your work informed on their terms — impact and
dates, not mechanism — so they never have to ask, and never learn of a slip late.

## Core Techniques

### 1. Map Stakeholders by Interest and Influence
Four tiers, four different treatments. Put every named person in exactly one.

| | Low interest | High interest |
|---|---|---|
| **High influence** | Keep satisfied — VP Eng, CFO. Monthly 3-line summary. Contact directly only for decisions above your authority. | Manage closely — your director, the PM, the partner team lead consuming your API. Weekly written update; ad-hoc on any change to date or scope. |
| **Low influence** | Monitor — adjacent teams, the sales floor. Quarterly release note. No push. | Keep informed — support lead, the two beta customers. Weekly digest, plus a direct note when their specific thing changes. |

The common mistake is treating "high influence" as "needs detail". A CFO with
low interest wants three lines a month; sending them your sprint report
guarantees they have stopped reading by the month you actually need them.

### 2. Deliver Slippage the Day You Believe It

```
❌ (sent 2 days before the date) "Unfortunately we're not going to make
    Friday. The integration work turned out bigger than expected."

✅ (sent 5 weeks out, the day the evidence appeared)
   Mar 14 launch is at risk; current estimate Mar 28, 70% confidence.
   Cause: the vendor's sandbox has been down since Feb 3 (their ticket
   #4471), so the payment path is untested. Nothing else has slipped.
   Doing about it: building against a recorded mock this week, so only
   final verification waits on them.
   Need from you: nothing yet. If they're still down on Feb 24 I'll ask
   you to escalate through their account team.
   Next update: Feb 24, or sooner if this changes.
```

Late bad news costs trust twice — once for the slip, once for the surprise.
Early news buys the stakeholder the only thing they actually want: options.

### 3. Translate Risk Into Their Consequence, Not Your Symptom

| What you'd say | What lands |
|---|---|
| "The job queue is backing up." | "Orders confirm 40 minutes late. Support volume roughly triples during a promo." |
| "We're at 85% disk on the primary." | "In about 9 days writes stop and the store goes read-only. Fixing now is 4 hours; fixing then is a weekend outage." |
| "Billing has 20% test coverage." | "Two of the last three billing incidents passed review unnoticed. Each cost finance about a day of reconciliation." |

The rule: name the effect on money, on customers, or on someone's calendar. If
you cannot name which of those three moves, you may not have a real risk yet.

### 4. Say No by Handing Back the Trade-Off
Never refuse on capacity. Convert the request into a choice that is theirs.

```
❌ "We can't take that on this quarter, the team's fully committed."

✅ "Yes — and here's the price. Exports is ~3 weeks. The quarter holds
    the SSO work (4 enterprise accounts blocked on it) and the search
    rebuild. To fit exports I'd push search to Q3. That's the trade I'd
    recommend against, but it is yours to make.
    If both must ship, I need a second engineer by the 10th — after
    that the ramp-up doesn't pay back inside the quarter."
```

"No" invites negotiation with your judgment. A priced choice invites a decision.

### 5. Run a Standing Update That Pre-Empts the Question
Same channel, same day, same shape, every week — including weeks when nothing
changed. Five lines: position against the previously stated date, what moved,
what's next, risks with owners, need-from-you. When the update is reliable
people stop pinging mid-week. Skip one and they assume the worst and start asking.

### 6. Manage Up Without Escalating Everything
Escalate for a decision above your authority, a resource you cannot obtain, or
when someone else's plan rests on a date you know is wrong. Do not escalate to
share anxiety or to hand back a decision that is yours. Always bring your
recommendation — `technical-communication` has the options-with-costs structure.
A manager who receives problems without recommendations learns to route work
away from you.

## Warning Signs

- A stakeholder learns about a slip from someone other than you
- The same person asks "where are we on X?" more than once a month
- Updates describe engineering activity rather than customer or revenue effect
- Requests refused with "we're at capacity" instead of a priced trade-off
- Every stakeholder receives the identical message at the identical depth
- Risks stated with no owner, no date, and no consequence in their terms
- Bad news held for the weekly meeting instead of sent the day it's known
- Escalations that arrive as questions rather than recommendations
- A "quick sync" requested because the written update was too vague to act on
