# Competitor Analysis (Verbose)

## Core Patterns

### Mapping the Real Competitive Set

Ask a team to name their competitors and you get three funded startups they read
about on Hacker News. Ask their lost prospects what they chose instead and you
get a very different list.

| Type | What it is | Why it wins | How you counter |
|---|---|---|---|
| Direct | Same category, same buyer | Feature depth, brand, incumbency | Positioning and segment focus |
| Indirect | Suite with your capability as one module | Already purchased; consolidation pressure | Depth on the job they treat as a checkbox |
| Substitute | Spreadsheet, shared doc, Airtable | Free, flexible, zero adoption friction | Scale, audit, collaboration, correctness |
| Services | Agency, contractor, offshore ops | No change management; someone else's problem | Cost curve and turnaround time |
| Internal build | A script the platform team owns | Feels free; fits exactly | Total cost of ownership, maintenance burden |
| Status quo | Do nothing | Costs nothing today; no risk | Quantify the cost of inaction |

In most B2B categories under ten years old, the top two "competitors" by deal
volume are a spreadsheet and doing nothing. This changes the work substantially.
Against Excel you are not fighting a feature gap — you are fighting infinite
flexibility, zero cost, and universal familiarity. You win on the things a
spreadsheet is structurally bad at: concurrent editing without version chaos,
audit trails, validation, permissions, volume, and not being emailed around as
`final_v3_REALFINAL.xlsx`. You lose on setup time and ad-hoc changes, so your
onboarding has to be near-instant or the substitute wins by default.

Against "do nothing", the entire sale is quantifying the cost of inaction, and
your competition is the buyer's other priorities, not another vendor.

### The Positioning Matrix

Build it around buyer evaluation criteria, sourced from win/loss interviews, not
from anyone's release notes. Score honestly — a matrix where you win every row
is a marketing asset, not an analysis.

```
Market: mid-market revenue reconciliation, 50–500 employees
Sources: 14 win/loss interviews (Q1–Q2), public pricing, 4 hands-on trials
Last verified: 2026-06-30
```

| Buyer criterion | Weight | Us | Rival A | Rival B | Spreadsheet |
|---|---|---|---|---|---|
| Time to first reconciled close | High | 1 day | 6 weeks | 3 days | Immediate |
| Explains *why* records differ | High | Yes | Partial | No | Manual |
| SOC 2 Type II + audit log | High | Yes | Yes | No | No |
| Volume ceiling | Medium | 10M rows | 50M | 1M | ~500k |
| ERP connectors | Medium | 4 | 20 | 2 | n/a |
| Custom rule engine | Medium | Basic | Deep | None | Total |
| 20-seat annual cost | Medium | $7.2k | $48k + $15k impl | $4.8k | $0 |
| Named support contact | Low | Yes | Yes (paid tier) | No | n/a |

Read the matrix in three passes:

1. **Table stakes** — rows where everyone scores the same. Necessary, never
   differentiating. Losing one of these loses deals; winning it wins nothing.
2. **Their moat** — rows where a rival is clearly ahead (Rival A's 20
   connectors). Decide deliberately whether to contest or concede; conceding
   loudly is a strategy, since it defines who you are not for.
3. **Your position** — rows where you are alone (explains *why* records differ,
   one-day time to value at a quarter of the price). This is your messaging.
   If there is no such row, you have a pricing problem, not a positioning one.

Weight the criteria from win/loss evidence. Unweighted matrices imply that
connector count and audit compliance matter equally, which no buyer believes.

### Why Feature Parity Loses

The parity trap runs predictably. A rival ships a feature. Sales says it cost
them three deals. It goes on the roadmap. Two quarters later you ship it, they
have shipped two more things, and you have spent a year executing their roadmap
while your differentiator stood still. Meanwhile your buyers, who chose you for
a reason, got nothing that reinforces that reason.

The asymmetry is that copying is always slower than announcing. You are also
copying a decision made with information you do not have — their feature may
have been built for one large customer's renewal and may be quietly deprecated.

Copy only when all three hold:

1. Win/loss interviews with *buyers* name the gap as decisive in ≥ 3 deals.
2. The gap blocks a job your target segment genuinely has.
3. Building it does not consume the capacity funding your differentiator.

Otherwise, reframe. If they have 20 connectors and you have 4, do not chase 16
more — cover the four your segment actually uses and compete on setup time,
publishing your own numbers so the comparison happens on your axis.

### Where Differentiation Is Durable

| Basis | Durable? | Why |
|---|---|---|
| UI polish | No | Copyable in a quarter |
| A single feature | No | Copyable; usually faster than you built it |
| Speed of shipping | Briefly | Erodes as you grow |
| Segment specialisation | Yes | A generalist cannot ship 30 industry workflows |
| Business model | Yes | Migrating pricing damages their existing revenue |
| Architecture | Yes | Real-time vs batch is a multi-year rewrite for them |
| Proprietary data / network | Yes | Accumulates with usage; cannot be bought |
| Distribution lock | Often | Exclusive integrations, channel, community |
| Switching costs | Yes | Data gravity, embedded workflows, trained staff |

The test for durability: *what would it cost this competitor to neutralise this,
and what would it break for them?* A rival with 400 enterprises on annual
per-seat contracts cannot introduce usage-based pricing without a revenue
shock, a sales-comp rewrite, and an angry renewal cycle. They know it is better
and still cannot do it — that is a moat. "We're easier to use" costs them one
redesign, so it is a lead, not a moat.

### Pricing and Packaging Analysis

List price is the least informative number on the page. Reconstruct the real
economics:

```
Per competitor, record:
  Metric          seat | usage | % of revenue processed | flat | hybrid
  Entry price     published, and what it excludes
  Tier gates      the specific feature that forces the upgrade
  Effective cost  modelled at 10 / 50 / 200 seats, annual
  Hidden costs    implementation fee, minimum commit, overage rate,
                  premium support, connector fees, sandbox fees
  Discounting     depth visible in public sector contracts, G2 reviews,
                  and reported by your own lost deals
  Free tier       what it permits, and where the wall sits
  Contract terms  annual only? auto-renew? multi-year lock?
```

Two questions produce most of the insight:

**What is gated, and does the gate feel fair?** The feature just above the line
is a strategic statement. SSO behind an enterprise tier three times the price is
the canonical resented gate, and pricing it into a lower tier is a positioning
move that costs almost nothing to build.

**Does the metric track the value delivered?** When a competitor charges per
seat but the value scales with transaction volume, high-volume/small-team
customers overpay dramatically. Those customers are acquirable with a metric
that fits them, and the incumbent cannot follow without repricing their base.

Model the crossover point explicitly: "below 25 seats they are cheaper; above
40 we are cheaper and the gap widens." Sales needs the number, and so does your
own packaging design.

### Win/Loss Interviews

The highest-value competitive input, and the most commonly skipped. Reps report
price as the loss reason in roughly half of all losses because it is the
explanation that implicates nobody.

Rules: interview the buyer, not the rep; use someone with no quota (product,
research, or an outside firm); run it 2–4 weeks after the decision, before
memory decays and after the emotion fades; interview wins as well as losses.

```
Framing (1 min)
  "We're not trying to change your decision — it's made. I want to
   understand our product's gaps. Fifteen to twenty minutes."

Trigger and process (5 min)
  - What made you start looking? What changed?
  - Who was involved? Who had a veto?
  - What was the shortlist? What dropped off early, and why?

The decision (8 min)
  - What made you choose them? If it came down to one thing, what?
  - Where did we look weakest?
  - Was there a moment you ruled us out? What happened just before?
  - If we had been free, would you still have chosen them?
  - What did their demo show that ours didn't?

Counterfactual (4 min)
  - What would have had to be true for us to win?
  - Anything you expected us to have and were surprised we didn't?
  - How did our pricing compare on the way you actually evaluated it?

Close (2 min)
  - Would you be open to a check-in in six months?
```

The "if we had been free" question is the workhorse. A buyer who says they would
*still* have chosen the rival has told you the loss was never about price, no
matter what the CRM says.

Tag every interview to a loss reason from a fixed taxonomy and review the
distribution quarterly. Twelve interviews is enough to see a pattern; one
memorable loss is not, and one memorable loss is usually what is driving the
roadmap.

### Keeping It Current

Big annual competitive decks are stale in six weeks, read once, and cited for a
year. Replace with a living one-pager per competitor.

```
Rival A — last verified 2026-06-30 by @javen
Position:    Enterprise reconciliation for 1,000+ employee finance orgs
Pricing:     $200/seat/mo, 25-seat minimum, $15k implementation
Strengths:   20 ERP connectors, deep rule engine, brand trust with auditors
Weaknesses:  6-week onboarding, no self-serve, poor sub-100-seat economics
We win when: buyer needs value inside a month, or is under 100 seats
They win when: 20+ source systems, or procurement demands a known brand
Recent:      2026-05 shipped SSO on the mid tier; hiring 4 mobile engineers
Open question: is the mobile hiring a product line or an internal tool?
```

Cadence:

| Frequency | Activity | Effort |
|---|---|---|
| Automated | Alerts on changelog, pricing page, status page, job posts | Zero |
| Monthly | 30-min review: what changed, does it alter anything? | 0.5 hr |
| Quarterly | Win/loss distribution review; refresh the matrix | Half a day |
| Event-driven | Funding, acquisition, repositioning, 3 losses to one name | 1–2 days |

Job postings are the best public signal available: hiring four mobile engineers
and a mobile PM predicts a mobile product far more reliably than any roadmap
webinar. Pricing-page diffs and changelog RSS cover most of the rest.

Two hygiene rules that keep this honest: every claim carries a date and a
source, and the doc has a named owner. Unowned competitive intel decays into
folklore — "I heard they can't handle multi-currency" repeated for two years
after they shipped multi-currency.

Feed the output into `roadmap-prioritization` as evidence, not as a mandate, and
into positioning work via `stakeholder-communication`. Competitive analysis
informs decisions; it does not make them.

## Common Anti-Patterns

❌ **The 80-row feature checklist** — proves you have more checkboxes while you
lose the deals, because buyers weight six criteria and you scored eighty.
✅ A weighted matrix of buyer criteria sourced from win/loss interviews.

❌ **Ignoring substitutes** — you benchmark three funded rivals while every lost
deal went to Excel or to nothing.
✅ Track substitutes and status quo as first-class rows in the loss taxonomy.

❌ **Roadmap by competitor** — "Rival A has it" as the entire justification.
✅ Require buyer-sourced evidence that the gap is decisive in named deals.

❌ **Intel from their marketing site** — you learn their positioning, which is
the one thing you already knew.
✅ Trials, win/loss interviews, support forums, review-site complaints, job posts.

❌ **Loss reasons from reps** — price gets blamed for everything.
✅ Buyer interviews by a non-quota-carrying interviewer, with the "if we were
free" control question.

❌ **Interviewing only losses** — you learn what is broken and never what works,
so messaging is built on guesswork.
✅ Interview wins too; wins reveal the message that landed.

❌ **List-price comparison** — nobody pays list, and the gap between tiers is
where the strategy is.
✅ Model effective cost at real seat counts, including implementation and minimums.

❌ **"Easier to use" as the differentiator** — every vendor claims it, none
prove it, and it is copyable in one redesign.
✅ Differentiate on something a competitor cannot adopt without self-harm.

❌ **Stale intel repeated as fact** — a two-year-old gap they closed last year.
✅ Dated, sourced claims with a named owner and a monthly review.

❌ **Competitive analysis as a quarterly ritual** — a deck produced, presented,
and never used in a decision.
✅ Tie each update to an open decision; if it changes nothing, cut the depth.

❌ **Panic responses to funding announcements** — a raise is not a shipped
product, and it is often the most-publicised thing a struggling company does.
✅ Watch hiring and shipping; those precede capability, funding does not.

## Competitive Analysis Checklist

- [ ] Competitive set includes substitutes, internal build, and "do nothing"
- [ ] Loss taxonomy has rows for spreadsheet and no-decision
- [ ] Matrix rows are buyer evaluation criteria, not feature lists
- [ ] Criteria weighted from win/loss evidence, not internal opinion
- [ ] At least one row where you are alone; if not, positioning is unresolved
- [ ] Table-stakes rows identified and explicitly not treated as differentiators
- [ ] Each claimed differentiator tested for what it would cost a rival to copy
- [ ] Deliberate decision on which rival strengths to concede
- [ ] Pricing modelled at 10 / 50 / 200 seats including implementation and minimums
- [ ] Tier gates identified, especially the resented one
- [ ] Pricing metric checked for alignment with delivered value
- [ ] Crossover point vs each rival computed and given to sales
- [ ] Win/loss interviews run by a non-quota interviewer, buyers not reps
- [ ] Wins interviewed as well as losses
- [ ] "If we were free, would you still have chosen them?" asked every time
- [ ] Loss reasons tagged to a fixed taxonomy and reviewed quarterly
- [ ] One-pager per competitor with a dated last-verified line and a named owner
- [ ] Automated alerts on changelogs, pricing pages, and job postings
- [ ] Every claim carries a source and a date
- [ ] Each refresh tied to an open decision it is meant to inform
