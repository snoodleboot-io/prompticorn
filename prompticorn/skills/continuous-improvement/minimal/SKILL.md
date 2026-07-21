# Continuous Improvement (Minimal)

## Purpose
Turn incidents, delivery friction, and retro complaints into tracked changes that measurably move a number — instead of into documents nobody reads twice.

## Core Techniques

### 1. Run Postmortems Blameless, and Mean It
Blameless does not mean avoiding the question of what happened. It means the write-up describes what a reasonable person did given the information available at the time, and then asks why that information made the action look correct.

- ❌ "Sam deployed without testing and took down checkout."
- ✅ "The deploy pipeline reported green while integration tests were skipped due to a cache miss, so the engineer had no signal that coverage was absent."

The second version produces a fix. The first produces a quieter engineer who will delay reporting the next one — which is how a 20-minute incident becomes a two-hour one. Every incident above your severity bar gets a postmortem within 5 business days, while people still remember.

Build the timeline first (see `incident-timeline-creation`), then find causes (see `root-cause-five-whys`). Do not do them in the same pass — reconstructing and explaining at once produces a narrative that fits the first theory anyone offers.

### 2. Give Every Action Item an Owner and a Date
An action item without a named individual and a due date is a wish. "The team will improve monitoring" has never once been done.
```
❌ Improve alerting on the payment service
✅ PRO-412 — Add p99 latency alert on /checkout at 500ms, 5m window
   Owner: Priya Raman   Due: 2026-08-07   Priority: P1
```
Rules that make it real: one named human, never a team or a rota; a date within one sprint for P1s; the ticket lives in the normal backlog with the same status workflow as feature work; and completion rate is reviewed monthly. If under roughly 70% of items land by their due date, you have an intake problem — you are generating more remediation than you have capacity to absorb, and the honest fix is fewer, larger items.

### 3. Measure Delivery With DORA — Real Definitions
| Metric | Definition | Elite | Low |
|---|---|---|---|
| Deployment frequency | Deploys to production per period | On demand, multiple/day | < monthly |
| Lead time for changes | First commit -> running in production | < 1 day | > 1 month |
| Change failure rate | Deploys causing degradation needing remediation | 0-15% | 40-60% |
| Failed deployment recovery | Time to restore service after a failed deploy | < 1 hour | > 1 week |

Two things make these useful rather than decorative. First, lead time starts at the *first commit*, not at PR open or ticket start — measuring from PR open hides the two weeks a branch sat unmerged. Second, throughput (the first two) and stability (the last two) must be read together; elite performers improve both, and a team optimizing deployment frequency alone will show it climbing while change failure rate climbs with it.

### 4. Instrument From Systems, Not Self-Reports
Derive metrics from git, the deploy pipeline, and the incident tracker. Survey-driven numbers drift toward whatever gets praised in the review. Compute lead time as the median (and p85) commit-to-deploy for each release, not an average — deployment distributions have long tails that an average flatters.

### 5. Review the Trend, Not the Number
A weekly number is noise. Look at rolling 4-week or quarterly trends, and pair every metric with the change it should have moved: "we added merge queues in April; lead time p85 went from 6 days to 2." A metric with no attached intervention is a dashboard, not an improvement program.

### 6. Never Use These Metrics to Compare Teams
The moment DORA numbers appear in performance reviews, they get gamed — deploys get split to raise frequency, incidents get reclassified to lower change failure rate. The metrics are a team's instrument for its own system. Compare a team to itself over time.

## Warning Signs

- Postmortems that name individuals, or that end at "human error"
- Action items with no owner, or owned by "the team"
- A backlog of remediation items older than 90 days that nobody triages
- Retro complaints that recur every sprint with no ticket attached
- DORA metrics collected but no intervention ever tied to them
- Lead time measured from PR open, hiding the real delay
- Deployment frequency reported without change failure rate
- Metrics used to rank teams or individuals
- Incidents below the severity bar never examined, so near-misses go unlearned
