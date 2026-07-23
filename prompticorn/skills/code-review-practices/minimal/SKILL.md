# Code Review Practices (Minimal)

## Purpose
Review code so defects are caught early and the author is unblocked fast — the second half is what most teams get wrong.

## Core Techniques

### 1. Label Every Comment With Its Severity
An unlabeled comment forces the author to guess whether they can merge.

```
blocking: This drops the transaction on the retry path — a partial write
          survives. Wrap lines 40-58 in the existing `with tx():` block.

question: Is `user_id` guaranteed non-null here? If a deleted user can reach
          this, the `.name` on line 22 raises.

nit: `fetchAll` → `fetch_all` for consistency with the rest of the module.
     Non-blocking, land it whenever.
```

Rule: if you cannot say what breaks, it is not `blocking:`. Authors may merge over any number of `nit:` comments.

### 2. Rewrite Vague Comments Into Actionable Ones

```
❌ "This feels overly complex."
✅ "The three nested conditionals on 88-104 all test `order.state`.
    A dict dispatch keyed on state would flatten it — happy to pair if
    you'd rather not."

❌ "Needs tests."
✅ "blocking: No test covers the empty-cart branch added on line 31,
    which is the case that produced last month's incident."
```

The test for a good comment: could the author act on it without asking a follow-up question?

### 3. Keep PRs Under ~400 Lines
Review quality falls off sharply with size. Reviewers find most defects in the first 200-400 changed lines of a sitting; past ~500 the comment rate drops not because the code got better but because attention ran out. A 1,200-line PR reliably gets "LGTM".

Split by seam: schema migration, then the service change, then the endpoint.

### 4. Optimize for Latency, Not Thoroughness
A PR waiting 2 days for review costs more cycle time than any defect it contains. Set a team norm: **first response within 4 business hours**, even if that response is "starting this afternoon." Review before starting your own new work.

### 5. Review What a Linter Cannot
Skip formatting, naming style, and import order — CI owns those. Spend human attention on:
- Is this the right problem to solve, in the right place?
- What happens on the failure path, on retry, on partial write?
- Does this make the *next* change harder? (See `incremental-implementation`.)
- Data lifecycle: migrations, backfills, rollback story.

### 6. Author-Side: Pre-Review Your Own Diff
Read your diff on the PR page before requesting review. Leave inline comments explaining non-obvious choices. Put the *why* in the description — the diff shows what changed, only you know what you rejected and why.

## Warning Signs

- Comments with no severity marker, so every one reads as blocking
- PRs sitting > 24h with no first response
- Median PR over 500 changed lines
- Review comments about formatting that CI could enforce
- "LGTM" within 60 seconds on a large diff
- Reviewers rewriting the change as the one they'd have written
- Debate resolved in DMs, leaving no record on the PR
