# Competitor Analysis (Minimal)

## Purpose
Work out where you can win rather than cataloguing what everyone else shipped —
and remember that the thing beating you is usually a spreadsheet, not a rival.

## Core Techniques

### 1. Count Substitutes, Not Just Competitors
A competitor sells a product like yours. A substitute is anything the buyer
currently uses instead — and it wins most deals in a young category.

| Category | Example |
|---|---|
| Direct competitor | Another vendor in your category, sold to the same buyer |
| Indirect competitor | A broader suite with your feature as a checkbox |
| Substitute | Excel, Google Sheets, Airtable, a Notion database |
| Services substitute | An agency, a contractor, an offshore ops team |
| Internal build | A script the platform team maintains |
| Do nothing | Live with the problem; the most common loss of all |

If your win/loss data has no "Excel" and no "did nothing" rows, you are not
tracking losses honestly. The correct response to a spreadsheet incumbent is
different from the response to a funded rival: spreadsheets lose on
collaboration, audit, and scale, and win on flexibility and zero adoption cost.

### 2. Build a Positioning Matrix, Not a Feature Checklist
Score against what buyers evaluate, not the union of everyone's release notes.
Rows should be jobs or outcomes; add a "who wins" column with a reason.

| Dimension | Us | Rival A (enterprise) | Rival B (SMB) | Spreadsheet | Who wins |
|---|---|---|---|---|---|
| Time to first value | 10 min | 6-week onboarding | 15 min | Instant | Spreadsheet, then us |
| SOC 2 / audit trail | Yes | Yes | No | No | Tie with A |
| Handles 10M rows | Yes | Yes | Degrades | Fails at 500k | Us and A |
| Price at 20 seats | $600/mo | $4,000/mo + services | $400/mo | $0 | B, then us |
| Custom workflow logic | Limited | Deep | None | Total | Rival A |
| Fixes the actual reconciliation job | Yes | Partly | No | Manual | Us |

The last row matters more than the rest. Parity rows are table stakes; the row
where you are alone is your position.

### 3. Differentiate Where They Structurally Cannot Follow
Feature parity is a losing race: whatever you copy takes a quarter, they copy
back in a quarter, and you have spent a year converging on their roadmap while
your own buyers got nothing new. Copy a feature only when its absence is
genuinely killing deals — and verify that in win/loss data, not from the sales
team's most recent bad week.

Durable advantages come from things a competitor cannot adopt without damaging
themselves:

- **Business model** — usage pricing against their per-seat revenue base
- **Architecture** — real-time where they batch, and rebuilding costs them years
- **Segment focus** — a workflow for one industry their generalist product cannot ship
- **Data or network effects** — accumulate with your users, not purchasable
- **Distribution** — an integration, channel, or community that is exclusive in practice

A rival with 400 enterprise customers on annual seat contracts cannot switch to
self-serve usage pricing without wrecking a quarter. That is a real moat.
"Better UX" is not — it is a lead, not a moat.

### 4. Analyse Packaging, Not Just Price
The list price is the least interesting number. What matters is what forces the
upgrade and what the buyer actually pays.

Record per competitor: the pricing metric (seat, usage, revenue percentage,
flat), what gates the next tier, the effective annual cost at 10 / 50 / 200
seats, discount depth visible in public procurement records, what is bundled
free that you charge for, and mandatory extras like onboarding fees or minimums.

The revealing questions: which feature sits just above the line customers most
resent, and does the pricing metric grow with the value the customer receives?
A tool priced per seat while value scales with data volume punishes exactly the
successful customers — and that misalignment is an opening you can price into.

### 5. Run Win/Loss Interviews
Ask the buyer, not your rep. Reps report price as the reason for almost every
loss because it is the least personal explanation available.

Script, 20 minutes, run by someone with no quota, 2–4 weeks after the decision:

- "Walk me through how the evaluation started. What triggered it?"
- "Who else was in the room, and who had veto power?"
- "What was the shortlist, and what dropped off early? Why?"
- "What made you pick them? What was the single deciding factor?"
- "Where did we look weakest?"
- "If we'd been free, would you still have chosen them?" (separates price from value)
- "What did they show you in the demo that we didn't?"
- "What would have had to be true for us to win?"

Interview wins as well. Wins tell you the message that landed, which is what
marketing needs and what nobody ever collects.

### 6. Keep It Current Without It Becoming a Chore
Annual 40-page decks go stale in six weeks and get read once. Maintain a
one-page-per-competitor living doc instead, with a dated last-verified line.

Cadence that survives contact with reality: automated alerts on changelogs,
pricing pages, and job postings (hiring six iOS engineers announces a mobile
push more reliably than any roadmap statement); a 30-minute monthly review of
what changed and whether it alters anything; a deeper refresh only when a
deal-affecting event occurs — a funding round, an acquisition, a repositioning,
or three losses to the same name in a quarter.

## Warning Signs

- A feature matrix with 80 rows, where you win on 60 and lose every deal
- No substitute or "did nothing" rows in the loss data
- Roadmap items justified only by "Competitor X has it"
- Competitive intel gathered entirely from competitor marketing pages
- Win/loss reasons collected from reps rather than buyers
- Positioning claims like "easier to use" with no evidence a buyer said it
- A deck last updated eleven months ago, cited as current
- Tracking five funded startups while losing to Excel
- Pricing benchmarked on list price with no view of actual discounts
