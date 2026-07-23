# Technical Communication (Minimal)

## Purpose
Write so a skimming reader gets the decision in the first two lines and the evidence only if they want it.

## Core Techniques

### 1. Bottom Line Up Front
The first sentence is the conclusion or the ask. Never the chronology.

```
❌ "Last week we started looking into the checkout timeouts. We tried
    raising the pool size, which didn't help, then Priya suggested
    profiling the gateway calls, and after some digging it turns out
    the retry logic is the issue. We think we can fix it."

✅ "Checkout timeouts are caused by unbounded retries in the payment
    gateway client. Fix is ~2 days; I need a decision on whether to
    ship behind a flag or wait for the release train.

    Detail: pool size was a red herring; profiling showed 3 nested
    retry layers producing up to 27 attempts per checkout."
```

Same facts, one third the reading time to the part that needs action.

### 2. Rewrite a Status Update

```
❌ "Making good progress on the migration. Ran into some issues with
    the legacy adapter but working through them. Should be done soon."

✅ Migration: on track for Thu 24th (was Tue 22nd — 2-day slip).
   Done: 6 of 8 services cut over.
   Left: reporting, billing.
   Slip cause: legacy adapter double-encodes UTF-8; fixed, but cost 2 days.
   Need from you: nothing.
```

"Good progress" and "soon" carry zero information. Dates, counts, and an
explicit "need from you" line carry all of it. Always include that line even
when the answer is "nothing" — its absence is what makes readers open the thread.

### 3. Escalate With an Ask, Not a Feeling

```
❌ "I'm getting pretty worried about the launch timeline, there's a lot
    still outstanding and I don't think people realize how much."

✅ Escalating: the Nov 3 launch is at risk. Recommend moving to Nov 17.
   Why: SSO integration is 3 weeks of work with 1.5 weeks left; the
   vendor's staging environment has been down since Oct 12 (ticket #4471).
   Options:
     A. Move to Nov 17 — my recommendation, no scope loss
     B. Launch Nov 3 without SSO — 4 enterprise accounts blocked
     C. Add a second engineer — saves ~4 days, not enough alone
   Decision needed by: Fri Oct 24, or option A becomes the only choice.
```

An escalation without a recommendation and a deadline is just anxiety
forwarded upward.

### 4. Write for the Skimmer
Assume the reader gives you 15 seconds and reads only bold text, the first line
of each paragraph, and headings. Front-load every paragraph. Use tables for
anything with more than three comparable items. Keep paragraphs under 5 lines.
If a document must be read start to finish to make sense, it will not be read.

### 5. State Uncertainty as a Range With a Reason

```
❌ "Should take about a week."
✅ "3-8 days. Low confidence — I haven't seen the auth code yet.
    If it uses the standard middleware it's 3; if it has a custom
    session layer it's 8. I'll know within a day of starting."
```

Give the range, the confidence, what drives each end, and when the uncertainty
resolves. A single-point estimate silently converts your guess into someone
else's commitment.

### 6. If It Isn't Written, It Didn't Happen
A decision made in a call exists only for the people on the call, and only until
they forget. Post the decision, the reasoning, and the rejected alternatives to
a durable place within the hour. The rejected alternatives are the part that
saves you re-arguing it next quarter.

## Warning Signs

- The ask appears in the last paragraph, or not at all
- "Good progress", "soon", "some issues", "almost done"
- Single-point estimates with no confidence attached
- Status updates that narrate effort instead of stating position and date
- A decision that exists only in a meeting or a DM thread
- Design docs circulated after the code is written
- Escalations that describe a worry without a recommendation or a deadline
