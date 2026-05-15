# Performance Workflow (Minimal)

## Purpose
Identify and resolve performance bottlenecks through systematic measurement, analysis, and optimization.

## Steps

### 1. Measure Baseline
- Identify the slow operation (endpoint, query, function)
- Measure current performance (response time, throughput, resource usage)
- Document baseline metrics with specific numbers
- Set target performance goal

### 2. Profile to Identify Bottlenecks
- Use profiler appropriate for language (py-spy, perf, Chrome DevTools)
- Run profiler against representative workload
- Identify top 3 slowest operations by time spent
- Categorize bottleneck type (CPU, I/O, network, database, memory)

### 3. Prioritize Bottlenecks
- Rank by impact (time saved × frequency of operation)
- Consider implementation effort (low-hanging fruit first)
- Focus on bottlenecks that account for >10% of total time

### 4. Optimize
- Apply targeted optimization for bottleneck type
- Make smallest change that addresses bottleneck
- Keep original implementation for comparison

### 5. Measure Improvement
- Re-run profiler with same workload
- Compare new metrics to baseline
- Verify improvement meets target goal
- Check for regressions in other areas

### 6. Document
- Record baseline, bottleneck, fix, and improvement
- Note any tradeoffs (complexity, memory, maintainability)
- Update performance documentation
- Add performance test to prevent regression