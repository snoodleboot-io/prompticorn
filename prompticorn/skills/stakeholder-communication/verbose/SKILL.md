# Stakeholder Communication (Verbose)

## Core Patterns

### The Stakeholder Map

A stakeholder is anyone whose plans change based on what your team does. That is
a longer list than the people in your standup: the PM, the support lead who
absorbs the complaints, the partner team building against your API, the finance
analyst whose forecast assumes a launch date, the two design-partner customers.

Plot each on interest (how much they care about the detail) against influence
(how much their opinion changes what you do). The quadrant sets the cadence and
the depth — not their seniority.

| Quadrant | Who, typically | Cadence | Depth | Escalation path |
|---|---|---|---|---|
| High influence / high interest | Your director, the PM, the tech lead of a consuming team | Weekly written; immediate on any date or scope change | Full: dates, risks, trade-offs, what you need | Direct, any time |
| High influence / low interest | VP Eng, CFO, the exec sponsor | Monthly, 3 lines | Position, one number, one risk | Only for decisions above your authority |
| Low influence / high interest | Support lead, beta customers, adjacent on-call | Weekly digest + direct note when their thing moves | Customer-visible behaviour and workarounds | Through the PM |
| Low influence / low interest | Sales floor, distant teams | Quarterly release note | Headline capability only | None |

Two mistakes dominate. The first is equating influence with appetite for detail:
the exec sponsor gets the sprint report, stops reading it in week three, and is
then genuinely surprised in month four. The second is under-serving high-interest
/ low-influence people — usually support. They have no power to change your
roadmap, which is exactly why teams neglect them, and they are the ones who find
out first when a release breaks something.

Re-draw the map when the org changes. A stakeholder who moved teams and kept
receiving your update is noise; a new director who is not on it is a landmine.

### The Standing Update

The purpose of a standing update is not to inform. It is to stop people asking.
That only works if it is predictable — same channel, same day, same shape, every
single week, including the weeks when nothing happened. An update that appears
only when there is news trains readers to interpret silence as trouble, which
means they ask anyway.

```
✅ Payments Migration — weekly, Thu

   Position:  On track for Mar 28 (unchanged from last week).
   Moved:     Refunds path cut over Tue; 3 of 5 flows now on the new
              processor. Zero customer-visible errors since.
   Next:      Subscriptions flow (est. 6 days), then disputes.
   Risks:     Vendor sandbox still down (their #4471, no ETA). Owner:
              me. Mitigation: recorded mock in place, only final
              verification is blocked. Becomes a date risk on Feb 24.
   Need from you: approval for the 15-minute write freeze, Mar 26
              06:00 UTC. Reply by Mar 19 or I'll schedule it as read-only
              degrade instead.
```

Note what each line does. "Position" always states the date and its delta
against the previously communicated date, so nobody has to diff two emails.
"Risks" names an owner and a date at which the risk converts into a schedule
change — a risk with neither is decoration. "Need from you" carries a default
action if nobody replies, so a silent stakeholder cannot block you.

Write "Need from you: nothing" in the weeks when it is nothing. Its absence is
what makes people open the thread and ask.

### Communicating Slippage

The single most damaging thing you can do to a stakeholder relationship is let
someone find out late about something you knew early. The slip itself is
forgivable — schedules are estimates. Discovering that you knew for three weeks
is not, because it tells them your other reports may also be stale.

The rule: communicate the day your belief changes, not the day the date arrives,
and not when you have a fix. You do not need a solution to send the message.

```
❌ Sent two days before the deadline

"Hi — unfortunately we're not going to make Friday for the payments
migration. The integration work turned out to be bigger than expected
and there were some issues with the vendor. We're working hard on it
and I'll let you know when we have a new date."
```

Everything here is wrong in a specific way. It arrives when no option remains.
"Bigger than expected" names no cause. There is no new date, so the reader
cannot plan; there is no confidence level, so when the new date arrives they
will not know how much to trust it either. "Working hard" is effort narration.

```
✅ Sent five weeks out, the day the evidence appeared

Subject: Payments migration — Mar 14 at risk, recommending Mar 28

Mar 14 is at risk. My estimate is now Mar 28, at 70% confidence.

Cause: the vendor's sandbox has been down since Feb 3 (their ticket
#4471, no ETA from them). The payment-authorisation path cannot be
tested end to end until it returns. Everything not touching the vendor
is on or ahead of schedule.

What I'm doing: building against a recorded mock this week so that
implementation continues; only final verification is blocked on them.
That caps the exposure at roughly 5 working days.

What I need from you: nothing today. If the sandbox is still down on
Feb 24, I'll ask you to escalate through their account team — that is
the point where it starts consuming float.

What would change this: sandbox back before Feb 24 puts Mar 14 back in
play at about 50%. Down past Mar 6 and Mar 28 becomes optimistic; I'd
come back with an Apr date.

Next update Feb 24, or immediately if anything changes.
```

The last section is what turns a slip notice into a planning instrument. The
reader now knows the trigger dates, so they can decide themselves whether to
hold their downstream commitments or renegotiate them now.

### Translating Engineering Risk Into Business Impact

Stakeholders outside engineering do not lack intelligence — they lack the model
that makes your symptom meaningful. "The queue depth is growing" is a fact about
a system they cannot see. Convert every risk into an effect on money, on
customers, or on someone's calendar. If it maps to none of the three, you may
not have a business risk yet, and you should handle it as engineering work
rather than escalate it.

| Engineering symptom | Business translation |
|---|---|
| "The job queue is backing up." | "Order confirmations arrive 40 minutes late. Support volume roughly triples during a promo, and about 6% of those customers reorder because they think it failed." |
| "We're at 85% disk on the primary." | "In about 9 days writes stop and the store goes read-only — no checkout. Four hours of work now, or a weekend outage then." |
| "Test coverage on billing is 20%." | "Two of the last three billing bugs shipped through review unnoticed. Each cost finance roughly a day of reconciliation and one of them refunded 300 customers twice." |
| "We have significant technical debt in the auth module." | "Any change to login takes 3 weeks instead of 3 days, and the SSO work four enterprise deals depend on is one of those changes." |
| "The vendor's API has no idempotency guarantees." | "A network blip during checkout can charge a customer twice. It has happened twice this quarter; each one is a chargeback plus a support escalation." |

Three properties make the right column work: a number, a named affected party,
and a comparison between acting now and acting later. Keep the mechanism
available for anyone who asks, but never lead with it — the mechanism is your
evidence, not their decision input.

Resist inflation. If you translate a minor risk into apocalyptic business
language, you win the argument once and lose calibration permanently. Say "this
is a 4-hour fix and a low risk, I'm telling you so it isn't a surprise later"
when that is what it is.

### Saying No to an Executive

A flat no invites negotiation about your judgment — how hard the work really is,
whether the team is really busy, whether you are being conservative. That
argument is unwinnable because they have more context on priorities than you and
you have more on cost. So do not have it. Give them the price and let them
choose, which is the decision they are actually equipped to make.

```
❌ "We can't take that on this quarter — the team is fully committed."
❌ "That's technically very difficult, it would take a long time."
❌ "Sure, we'll try to fit it in." (the worst one — it commits you to a
    date you have not thought about, and drops something silently)
```

```
✅ "Yes, and here is what it costs.

    The export feature is about 3 weeks of one engineer.

    The quarter currently holds: SSO (4 enterprise accounts are blocked
    on it, ~$180k ARR) and the search rebuild (support says search is
    the #1 complaint, 22% of tickets).

    To fit exports I would move the search rebuild to Q3. That is the
    trade I'd recommend against — search compounds and exports has a
    manual workaround via the CSV endpoint — but the call is yours.

    If exports and search both have to land this quarter, I need a
    second engineer by the 10th. After the 10th, ramp-up costs more
    than the engineer adds inside the quarter."
```

This does four things at once: it does not refuse, it names the real currency
(engineer-weeks), it exposes what would be given up in *their* units rather than
yours, and it states a recommendation while explicitly leaving the decision with
them. It also puts the third option — more capacity — on the table with an
expiry date, which is usually the option nobody remembers to raise.

Follow up in writing within the hour, whatever they decide. "Confirming: exports
in, search moves to Q3, revisit if support ticket volume on search exceeds 25%."
Verbal reprioritisation that is not recorded gets remembered as you dropping
search on your own initiative.

### Managing Up Without Escalating Everything

Escalate when one of three things is true: the decision is above your authority,
you need a resource you cannot obtain yourself, or another team is planning
against a date you know to be wrong. Otherwise, decide and report.

Everything else is either a decision you should make (and then note in your
update) or an anxiety you should resolve before writing. A manager who receives
a stream of unfiltered problems does one of two things: starts making your
decisions for you, or starts routing important work elsewhere. Both are worse
than being wrong occasionally.

When you do escalate, carry the recommendation, the options with their costs,
the decision deadline, and what evidence would reverse you. That structure is in
`technical-communication` and is not repeated here.

The counterpart skill is telling your manager things they have not asked about.
A brief "heads up: the payments vendor is flaky, I have it contained, no action
needed" costs you a line and buys you enormous latitude, because it establishes
that your silence means things are actually fine.

### Meetings, and How to Need Fewer

Most stakeholder meetings exist because the written artefact was insufficient.
Before accepting a recurring sync, ask what question it answers, then try to
answer that question in the standing update instead. Meetings that survive that
test are the ones with genuine decisions or genuine disagreement in them.

For the ones that remain: send the material 24 hours ahead with the decision
stated at the top, and open by naming the decision needed and the time budget.
End every one by reading back the decisions and owners — then post them in
writing within the hour, because a decision that lives only in a call does not
exist. See `technical-communication` for the durable-record format.

## Common Anti-Patterns

❌ **Same message to every stakeholder** — the CFO reads your sprint detail and
stops reading entirely; the support lead never hears that their workflow changed.
✅ Map by interest and influence. Four audiences, four cadences, four depths.

❌ **Holding bad news until you have a fix** — the stakeholder learns late and
now doubts every other status you have given them.
✅ Send the day your belief changes. A slip notice with no solution is still
useful; a late one with a solution is not.

❌ **Reporting engineering symptoms** — "the queue is backing up", "we have tech
debt", "coverage is low".
✅ Money, customers, or calendar: "orders confirm 40 minutes late, support volume
triples."

❌ **"We're at capacity"** — refuses on your authority and invites an argument
about whether the team is really busy.
✅ Price it and hand the trade-off back: "3 weeks; it would displace search;
here's what I'd recommend and why, but it's your call."

❌ **"Sure, we'll try to squeeze it in"** — commits to an unexamined date and
silently drops something else.
✅ Name what moves. Every yes has a displaced thing; say which.

❌ **The update that appears only when there is news** — silence gets read as
trouble, and people ask anyway.
✅ Same day, same shape, every week, including "nothing changed".

❌ **Risks with no owner and no trigger date** — decorative worry that everyone
learns to skip.
✅ Every risk carries an owner, a mitigation, and the date it becomes a schedule
change.

❌ **Escalating every problem upward** — the manager starts making your decisions
or stops giving you interesting ones.
✅ Escalate only for authority, resources, or someone else's wrong assumption —
and always with a recommendation.

❌ **Percentage-complete reporting** — "we're 80% done" for three consecutive
weeks, which is unfalsifiable and always precedes a slip.
✅ Counts of finished units and a date: "3 of 5 flows migrated, subscriptions
next, 6 days."

❌ **Verbal reprioritisation left unrecorded** — remembered next quarter as you
having dropped something unilaterally.
✅ Written confirmation of the trade within the hour, including what was traded
away and the revisit condition.

❌ **Surprising a stakeholder in a group setting** — raising their bad news in a
meeting they did not know was coming.
✅ No stakeholder should hear anything about their own area first in a room. Brief
them before.

## Stakeholder Communication Checklist

- [ ] Every stakeholder placed on the interest/influence map, with a cadence
- [ ] Map re-checked after any org change
- [ ] Standing update goes out on the same day and channel every week
- [ ] Update sent even in weeks where nothing changed
- [ ] Position line states the date and its delta against the last stated date
- [ ] Progress reported as counts of completed units, not percentages
- [ ] Every risk has an owner, a mitigation, and a trigger date
- [ ] "Need from you" line present, with a default action if nobody replies
- [ ] Slippage communicated the day the belief changed, not when the date arrived
- [ ] Slip notices carry a cause, a new date, a confidence, and trigger dates
- [ ] Every risk translated into money, customers, or calendar impact
- [ ] Impact stated with a number and a now-versus-later comparison
- [ ] Impact not inflated beyond what you'd defend under questioning
- [ ] Requests answered with a priced trade-off, never "we're at capacity"
- [ ] Every accepted request names what it displaces
- [ ] Verbal reprioritisations confirmed in writing within the hour
- [ ] No stakeholder hears news about their own area first in a group setting
- [ ] Escalations reserved for authority, resources, or others' wrong assumptions
- [ ] Recurring meetings tested against "could the written update answer this?"
- [ ] Meeting decisions posted to a durable place within the hour
