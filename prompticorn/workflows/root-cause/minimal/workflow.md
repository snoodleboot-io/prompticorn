---
name: "root-cause"
description: "Root cause analysis for bugs and incidents"
version: "1.0"
languages: ["python", "typescript"]
subagents: ["debug"]
---

# Root Cause Analysis Workflow (Minimal)

## Purpose
Systematically identify the root cause of bugs, errors, and incidents through evidence gathering and hypothesis testing.

## Steps

### 1. Gather Symptoms and Context
- What is the symptom vs expected behavior?
- What environment (local, staging, production)?
- Frequency (always, intermittent, under load, time-based)?
- When did it start (after deploy, change, or always existed)?

### 2. Collect Artifacts
- Error message and full stack trace
- Relevant code sections
- Logs before, during, and after failure
- Recent changes (git diff or description)
- Monitoring data (CPU, memory, network)

### 3. Form Hypotheses
- List 3-5 potential root causes ranked by likelihood
- For each hypothesis: what evidence supports it?
- For each hypothesis: what would rule it out?
- Identify the most likely hypothesis to test first

### 4. Test Hypotheses
- Design minimal experiment to confirm/rule out hypothesis
- Execute test with controlled conditions
- Observe results and compare to predictions
- If ruled out, move to next hypothesis

### 5. Identify Root Cause
- Confirm root cause with reproducible evidence
- Distinguish root cause from symptoms
- Verify by asking "Why?" 5 times
- Document the causal chain

### 6. Verify Fix
- Design fix that addresses root cause (not symptom)
- Test fix resolves the issue
- Verify no regressions introduced
- Add test to prevent recurrence
