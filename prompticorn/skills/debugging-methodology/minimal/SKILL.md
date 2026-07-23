# Debugging Methodology (Minimal)

## Purpose
Find the cause of a live defect by experiment rather than by guessing, using the cheapest test that can eliminate the most possibilities.

## Core Techniques

### 1. Run the Loop: Observe → Hypothesise → Experiment → Update
Write the hypothesis down before you test it. A hypothesis that cannot be wrong is not a hypothesis.

```
Observation:  Checkout 500s, but only for users with >50 cart items.
Hypothesis:   The cart serialiser times out above some item count.
Experiment:   Call the serialiser directly with 49 and 51 items, time it.
Result:       49 -> 40ms, 51 -> 12s. Hypothesis survives; boundary is not 50.
```

Pick the experiment that splits the remaining possibilities most evenly, not the one that confirms your favourite theory. Two minutes of thinking about which test to run beats twenty minutes of running the wrong ones.

### 2. Binary Search the System
Halve the space, not walk it. For a request failing somewhere across client → LB → API → cache → database, check the midpoint first: does the API log show the request arriving? One check eliminates half the stack.

Bisect by disabling: turn off half your middleware, half your feature flags, half your plugins. Whichever half still fails contains the cause.

### 3. Binary Search Time with `git bisect`
When "it worked last week", let git find the commit:

```bash
git bisect start
git bisect bad HEAD
git bisect good v2.14.0
# git checks out a midpoint; test it, then:
git bisect good     # or: git bisect bad
git bisect reset    # when it names the commit
```

Automate it with a script that exits 0 for good and 1 for bad:

```bash
git bisect run pytest tests/test_checkout.py::test_large_cart
```

Roughly 10 steps over 1000 commits. Use `git bisect skip` for commits that will not build.

### 4. "Works on My Machine" Is Data
It is not a dismissal — it is a confirmed difference between two environments, and the bug lives in that difference. Enumerate it: OS, runtime version, dependency lockfile, environment variables, data, clock/timezone, locale, network egress. Diff the two lists. The bug is on that diff.

### 5. Read the Stack Trace Properly
Read the *innermost* frame for what broke and the outermost of *your* frames for why. Skip library frames until you find the last line of your own code — that is where the bad value came from. For chained exceptions, the first "caused by" is usually the real one; the rest is wrapping. And read the exception message literally: `NoneType has no attribute id` means something returned `None`, so go find what.

### 6. Shrink Until It Is Obvious
Delete code until the bug disappears; the last thing you removed is implicated. Keep cutting the reproduction — fewer records, fewer services, no framework — until it fits in a single file you can hold in your head. A 10-line reproduction usually explains itself.

### 7. Choose the Right Instrument
- **Debugger** — when the state is complex and the repro is fast and local.
- **Logging** — when the bug is intermittent, in production, or spread across processes.
- **Tracing** — when latency or causality crosses service boundaries.
- **Core dump / profiler** — when the process hangs, crashes hard, or is simply slow.

### 8. Expect Heisenbugs
Adding a log line changes timing, allocation, and optimisation, so races and use-after-free bugs move or vanish when observed. If the bug disappears under instrumentation, that is evidence it is timing-dependent — record from outside the process (tracing, kernel counters, packet capture) rather than adding prints inside the race window.

## Warning Signs

- Changing code before you can state what you expect the change to prove
- "Fixing" by retry, restart, or `sleep`, with the cause still unknown
- A reproduction that takes ten minutes and is never shrunk
- Reading only the top line of the stack trace
- Dismissing "works on my machine" instead of diffing the environments
- Multiple changes made at once, so a passing test names no cause
- No record of which hypotheses were already ruled out

Once the defect is understood and fixed, the *systemic* cause belongs in a postmortem — see `root-cause-five-whys`.
