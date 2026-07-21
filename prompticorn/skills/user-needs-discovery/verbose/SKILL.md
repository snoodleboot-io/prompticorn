# User Needs Discovery (Verbose)

## Core Patterns

### The Mom Test: Ask About Behaviour, Not Opinions

The name comes from a simple test — could you ask this question of your own
mother and get a useful answer, given she loves you and wants you to succeed?
"Do you think my app is a good idea?" fails. "How did you handle that last
time?" passes, because the answer is a fact about her life, not a judgement of
your idea.

Three rules follow:

1. Talk about their life, not your idea.
2. Ask about specifics in the past, not generics or opinions about the future.
3. Talk less, listen more.

The failure mode is subtle. You do not usually walk in and ask "is this a good
idea?" — you ask "how important is X to you?", which is the same question in a
suit. Importance is an opinion. Frequency, cost, and last occurrence are facts.

### Writing the Interview Guide

Fifteen questions is too many for a 30-minute call. Aim for five or six openers
with follow-ups you improvise from. A working guide for a hypothetical
invoice-reconciliation product, aimed at finance ops leads:

```
Warm-up (3 min)
  - What's your role, and what does a normal week look like?
  - Which parts of month-end fall to you specifically?

The last occurrence (12 min)
  - Walk me through the last close. What day did it start, when did it finish?
  - Where in that did things go wrong? Tell me about the worst one.
  - What did you do when you found the discrepancy? Who did you have to talk to?
  - How long did that take? Was that typical or unusually bad?

Existing workarounds (8 min)
  - What are you using today to catch those? Can you show me?
  - Who else touches it? What happens when they're out?
  - Have you tried to fix this before? What happened to that attempt?
  - What did you look at and reject? Why?

Consequences and money (5 min)
  - What happens if the close slips two days?
  - Is there a budget line this comes out of? Who signs it?

Commitment (2 min)
  - Who else on your team should I talk to?
  - Would you be up for a 45-minute session with your actual data next week?
```

Note what is absent: the product is never described. If they ask what you are
building, answer briefly at the very end, after the useful information is
banked — a described solution contaminates everything said after it.

### Bad Question, Good Question

❌ "Would you use a mobile version of this?"
✅ "When was the last time you needed this and weren't at your desk? What did you do?"

❌ "How much would you pay for this?"
✅ "What are you spending on this problem today — tools, contractors, or hours?"

❌ "Do you think this feature would be useful?"
✅ "Tell me about the last time you needed to do that. How did you get it done?"

❌ "What features do you want?"
✅ "What's the last thing that made you swear at the screen?"

❌ "Is speed important to you?"
✅ "What do you do while the report is generating?"

❌ "Would you switch from your current tool?"
✅ "When did you last evaluate an alternative? What made you stay?"

The pattern is mechanical: strip out the hypothetical mood, add a time anchor,
and remove the noun you are hoping to hear.

### Recruiting the Right People

Bad recruiting invalidates perfect interviewing. Screen for the *behaviour*, not
the title — you want people who did the thing recently, not people who might.

| Screener question | Rejects |
|---|---|
| "How many times did you run a month-end close last quarter?" (need ≥ 2) | People describing the process secondhand |
| "Which tool did you personally open to do it?" | Managers who delegate the actual work |
| "Do you sign off, approve budget, or neither?" | Mismatched decision authority |

Sources ranked by bias: strangers matching the screener (best), inbound signups
who never activated, referrals from interviewees, your customers, your own
network (worst — they are motivated to encourage you).

Compensate strangers. An unincentivised recruit skews heavily toward people with
unusual amounts of free time or an axe to grind.

### Saturation and Sample Size

Discovery interviews are qualitative: the output is a *set of problem
categories*, not an estimate of a proportion. That determines when to stop.

| Interviews (single segment) | Typically yields |
|---|---|
| 1–5 | The obvious problems; guide still badly wrong |
| 6–10 | Most distinct categories; language starts repeating |
| 11–15 | New variations, few new categories — saturation |
| 16+ | Diminishing returns; spend it on a second segment instead |

Make it falsifiable rather than a feeling. After each interview, append any
*newly named* problem to a list. Track new-items-per-interview. When two
consecutive interviews add zero new categories, you are saturated for that
segment.

The trap is aggregation. Fifteen interviews spread across admins, finance leads,
and auditors is five per segment — not saturation anywhere. Segment boundaries
that reset the count include role, company size band, industry, and whether they
currently pay for a competing tool.

Note the sharp limit: saturation tells you what problems exist. It tells you
nothing about *how many* people have them. "9 of 12 interviewees mentioned X"
is not 75% of the market — see `user-testing-methods` for the qualitative vs
quantitative sample-size asymmetry.

### Stated Preference vs Revealed Behaviour

```
Stated   (interviews, surveys, feature votes)      -> hypotheses
Revealed (logs, billing, calendars, screen shares) -> evidence
```

Divergences worth expecting:

| They say | They do |
|---|---|
| "I want more customisation" | Never change a default setting |
| "Price is the main factor" | Choose the pricier plan with phone support |
| "I'd use the mobile app daily" | Install it, open it twice, stop |
| "The export is fine" | Export to CSV, then paste into a template every time |
| "We need integrations with everything" | Connect exactly one, usually Slack |

None of this makes interviewees liars. People are poor forecasters of their own
behaviour and describe their idealised self. The remedy is to design every
research plan so a stated finding gets checked against a behavioural one before
it reaches a roadmap — instrumentation, a fake-door test, or a screen share.

### Job Stories

A job story states a situation, a motivation, and an expected outcome:

> When **[situation]**, I want to **[motivation]**, so I can **[expected outcome]**.

Filled in from the interview guide above:

> When **the close is due Friday and our ERP and payment processor disagree on
> three days of revenue**, I want to **see exactly which transactions differ and
> what changed them**, so I can **correct them and sign off without a second
> late night**.

This is useful because it constrains design. Any solution has to work under a
deadline, has to explain *why* records differ (not just that they do), and has
to end in a sign-off action. A persona card reading "Finance Fiona, 34, likes
efficiency" constrains nothing.

Test each story against three checks: is there a trigger you could observe, is
the motivation solution-agnostic, and is there a real consequence if it fails?

### Synthesis

Do not synthesise from memory. Within 24 hours, pull verbatim quotes into rows —
quote, speaker, segment, date, and the problem category you assigned. Then group.

The discipline is that every claim in the readout traces to at least two quoted
sources from the same segment, and single-source findings are labelled as such.
A finding one person voiced strongly will otherwise dominate the room purely
because it was memorable.

Have a second person tag a sample of the quotes independently. Where the two
taggers disagree on categories, your scheme is describing your assumptions
rather than the data.

Discovery output feeds `feature-planning` and `requirements-specification`; it is
not itself a prioritised list. Deciding which problem matters most belongs to
`roadmap-prioritization`, and how you report it to `stakeholder-communication`.

## Common Anti-Patterns

❌ **Pitching, then asking for feedback** — everything after the pitch is a
reaction to your idea rather than a description of their life.
✅ Describe nothing until the last two minutes of the call.

❌ **"Would you use this?"** — a free, socially rewarded yes with no predictive
value.
✅ "Tell me about the last time you had this problem. What did you do?"

❌ **Leading questions carrying the answer** — "Don't you find the export
frustrating?" gets agreement from people who never export.
✅ "Talk me through what you do after the report finishes."

❌ **Interviewing only current happy customers** — they self-selected for liking
what already exists, so they cannot tell you why others bounced.
✅ Include churned users, evaluators who chose a competitor, and cold-recruited
strangers who match the behavioural screener.

❌ **Stopping at the complaint** — "reporting is painful" is not actionable.
✅ Chase to the workaround and its cost: what they built, who maintains it, what
it costs in hours or dollars per month.

❌ **Counting mentions as market sizing** — "8 of 10 said yes" from a hand-picked
sample of 10 is not 80% of anything.
✅ Interviews generate the hypothesis; a survey or instrumentation sizes it.

❌ **The founder interviewing alone with no recording** — memory reconstructs
toward the thing you hoped to hear.
✅ Two people, or a recording plus transcript, with quotes captured verbatim.

❌ **Personas built from demographics** — age and job title do not predict
behaviour in most B2B and much B2C.
✅ Segment by observed behaviour and job to be done.

❌ **Discovery that never ends** — twenty-eight interviews and no decision.
✅ A stated saturation rule up front, and a named decision the research unblocks.

❌ **Asking about frequency in the abstract** — "how often do you..." invites a
tidy invented number.
✅ Bound it: "how many times last week?", or count it in their tool together.

## User Needs Discovery Checklist

- [ ] The decision this research must unblock is written down before recruiting
- [ ] Screener selects on recent behaviour, not job title alone
- [ ] Recruits include non-customers and churned users, not just fans
- [ ] Guide contains no description of the proposed solution
- [ ] Every core question is anchored to a specific past event
- [ ] No question can be answered with a polite yes
- [ ] Interviews run in waves of ~5 with guide revision between waves
- [ ] Sessions recorded and transcribed, with a second listener or note-taker
- [ ] Existing workarounds probed for cost, owner, and prior fix attempts
- [ ] Each interview ends with a commitment ask (intro, pilot, next session)
- [ ] Saturation tracked as new-categories-per-interview, per segment
- [ ] Segment boundaries respected; counts not aggregated across roles
- [ ] Stated preferences flagged for behavioural verification before roadmapping
- [ ] Findings written as job stories with trigger, motivation, and consequence
- [ ] Every claim traced to ≥ 2 verbatim quotes, or marked single-source
- [ ] Category tagging spot-checked by a second person
- [ ] Quantitative claims deferred to a method that can support them
