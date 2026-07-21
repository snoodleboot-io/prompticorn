# User Testing Methods (Minimal)

## Purpose
Pick the testing method that can actually answer your question, and size it
correctly — most bad research is a good method aimed at the wrong question.

## Core Techniques

### 1. Match the Method to the Question

| Method | Answers | Cannot answer |
|---|---|---|
| Moderated usability (5–8 users) | Where and why people get stuck | How many people get stuck |
| Unmoderated usability (15–30) | Same, at scale and lower cost | Anything needing a follow-up "why" |
| A/B test (thousands) | Which variant converts better | Why it converts better |
| Diary study (8–15, 2–4 weeks) | Behaviour over time, in real context | Anything about a UI you haven't shipped |
| Card sort (15–30) | How users group and name concepts | Whether your navigation works |
| Tree test (30–50) | Whether people can find things in your IA | Whether the page itself is usable |
| Five-second test (20–50) | What a page communicates at a glance | Whether the flow completes |
| Survey (100s–1000s) | Distribution of stated attitudes | What people will actually do |

The single most common error is running a usability test to settle a question
about conversion rate, or an A/B test to learn why something confuses people.

### 2. Write Tasks, Not Instructions
A task gives a goal and a context. An instruction gives the steps, so it tests
whether the person can follow directions.

❌ "Click Settings, then Billing, then change your plan to Pro."
✅ "You've decided the free plan isn't enough for your team. Get yourself onto
the plan that includes SSO."

❌ "Find the export button."
✅ "Your accountant needs last quarter's transactions in a spreadsheet by
tonight. Get them what they need."

❌ "Do you find this dashboard easy to use?"
✅ "Your manager asks which campaign performed worst last month. Find out."

Rules: never name a UI element the participant must find, state a realistic
motive, and make success observable so you are not judging by vibe. Define the
success criterion before the session — "reaches the Pro checkout page" — not
after, when you are tempted to be generous.

### 3. Know the Sample-Size Asymmetry
Five users is the standard usability number because problem *discovery*
saturates fast: if a given flaw trips roughly 30% of users, five sessions have
about an 83% chance of exposing it at least once. You are asking "does this
problem exist?", and one occurrence is proof.

Five users tell you nothing about a rate. Estimating a proportion needs hundreds
because the margin of error scales with the square root of the sample. If 2 of 5
users fail a task, the exact (Clopper-Pearson) 95% interval on the true failure
rate runs from 5% to 85% — the observed 40% is nearly meaningless. To pin a rate
within ±5 points you need on the order of 400 observations.

So: qualitative methods find problems with few people; quantitative methods
measure them with many. Neither substitutes for the other.

### 4. Size A/B Tests Before Running Them
Detectable effect shrinks as sample grows, roughly with 1 over the square root of
n per arm. Rough intuition at 80% power, 5% significance, baseline conversion 5%:

| Relative lift to detect | Users per arm | Days at 2,000/day/arm |
|---|---|---|
| 20% (5.0% to 6.0%) | ~9,000 | ~5 |
| 10% (5.0% to 5.5%) | ~31,000 | ~16 |
| 5% (5.0% to 5.25%) | ~120,000 | ~60 |

Run the calculation first. If the honest answer is "eleven weeks", you cannot
A/B test this — decide another way, or test something with a bigger expected
effect. Also run whole weeks: weekday and weekend traffic differ enough that
five-day tests measure the calendar.

### 5. Do Not Peek
Checking significance repeatedly and stopping the moment p drops below 0.05
inflates the false-positive rate badly — with daily checks over a two-week test
the real rate lands near 20–30%, not 5%. Every look is another chance for noise
to cross the line, and random walks cross thresholds often.

Fix it with one of: fix the sample size and analyse exactly once; or use a
sequential method built for it (always-valid p-values, alpha spending) that
prices the peeking in. Monitoring for a guardrail breach or a crash is fine —
that is a safety stop, not an efficacy decision.

### 6. Shut Up During the Session
Facilitator silence is the whole skill. When someone pauses, count to ten before
speaking. When they ask "is this right?", say "what would you expect to happen?"
When they get stuck, let them stay stuck — that stuckness is your finding, and
your hint deletes it. Ask "what are you thinking?" not "was that confusing?"

## Warning Signs

- The method chosen before the question was written down
- Tasks that name the button, menu, or page the user is supposed to find
- Success judged after the fact by the person who designed the flow
- Percentages reported from five participants
- An A/B test with no pre-registered sample size or stopping rule
- Calling a test early because it "already looks significant"
- Tests running for 3 or 5 days rather than whole weeks
- Only new users tested, when the change mostly affects returning users
- Sessions where the facilitator explains the interface
- Findings that all confirm what the team already intended to build
