# Performance Optimization (Minimal)

## Purpose
Make a system measurably faster by finding where the time actually goes, rather than where you assume it goes.

## Core Techniques

### 1. Measure First — the Bottleneck Is Not Where You Guess
"Profile before optimizing" is not a platitude; it is the observation that experienced engineers guess wrong most of the time. The hand-written parsing loop you were going to rewrite in C is 3% of wall time, and 60% is a JSON serializer being called once per row inside a loop nobody noticed.

```bash
# Python: sampling profiler, no code changes, works on a live process
py-spy top --pid 4821
py-spy record --pid 4821 --duration 60 --output profile.svg

# Deterministic profile of a script
python -m cProfile -o out.prof script.py && python -m pstats out.prof
```

Profiling does not just rank your list — it changes the plan. Roughly one time in three, the profile shows the real fix is a config change or a removed call, and the optimization you scheduled a week for is unnecessary.

### 2. Set a Target Before You Start
"Faster" is not a goal. "p99 checkout latency under 300ms at 500 rps" is. Without a number you cannot tell when to stop, and optimization has no natural stopping point.

### 3. Know the Latency Budget You Are Spending
| Operation | Order of magnitude |
|---|---|
| L1 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| SSD random read | ~100 µs |
| Intra-datacenter round trip | ~0.5 ms |
| Disk seek (spinning) | ~10 ms |
| Cross-continent round trip | ~150 ms |

A remote call costs about 5,000× a memory reference. This is why removing one N+1 query beats any amount of loop tuning, and why the fix is almost always "do less I/O," not "make the CPU work faster."

### 4. Amdahl's Law Bounds Your Payoff
If a component is 20% of runtime, making it infinitely fast buys you 20%. Compute the ceiling before committing: a 10× speedup of a 5% component yields 4.5% overall. Always attack the largest contributor first, then re-profile — the ranking changes after every fix.

### 5. Optimize Complexity Before Constants
An O(n²) loop over a growing collection cannot be rescued by a faster language. Look for accidental quadratics: a membership test against a list inside a loop, string concatenation in a loop, a nested scan that should be a hash join.

```python
# O(n*m) — 40s at n=50k
dupes = [x for x in new_ids if x in existing_ids]      # existing_ids is a list

# O(n+m) — 0.02s, same result
existing = set(existing_ids)
dupes = [x for x in new_ids if x in existing]
```

### 6. Measure Tails, Not Averages
Average latency hides everything that matters. If p50 is 40ms and p99 is 2.5s, one request in a hundred is awful — and on a page making 100 backend calls, nearly every page load hits it. Report p50/p95/p99 and alert on p99.

### 7. Benchmark Honestly
Run against production-shaped data volumes, warm the cache, repeat the measurement, and report a distribution. A benchmark on 1,000 rows tells you nothing about behavior at 10 million, where the working set stops fitting in memory and the curve bends.

## Warning Signs

- Optimization work started without a profile
- No stated latency or throughput target
- Averages reported, percentiles absent
- Micro-optimizations landed while an N+1 query pattern remains
- Benchmarks run on toy data or a single iteration
- Caching added before the slow path was identified
- Performance measured only in dev, never in production
- Code made unreadable for a gain nobody quantified
