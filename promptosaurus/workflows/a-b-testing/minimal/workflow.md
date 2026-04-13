---
name: "a-b-testing"
description: "Structured experimentation process for data-driven decisions"
agent: "product"
category: "product"
related_workflows:
  - analytics-setup-workflow
  - feature-launch-checklist
---

# A/B Testing Workflow

## Goal
Run controlled experiments to validate product hypotheses with statistical rigor.

## Quick Steps

1. **Form Hypothesis**
   - Clear prediction statement
   - Expected impact on metrics

2. **Design Experiment**
   - Control vs variant(s)
   - Sample size calculation
   - Duration estimate

3. **Implement Test**
   - Feature flags setup
   - Random assignment logic
   - Tracking verification

4. **Monitor Execution**
   - Check data quality
   - Monitor for bugs
   - Ensure sample balance

5. **Analyze Results**
   - Statistical significance test
   - Practical significance assessment
   - Segment analysis

6. **Make Decision**
   - Ship, iterate, or abandon
   - Document learnings

## Key Frameworks

- **Statistical Significance:** p-value < 0.05
- **Minimum Detectable Effect:** Smallest meaningful change
- **Power Analysis:** Sample size for reliable results

## Success Factors

- Clear hypothesis before starting
- Sufficient sample size
- Test runs full duration
- Multiple metrics considered
- Results drive action

## Template Output

**Hypothesis:** Changing [X] will increase [metric] by [Y%]
**Result:** [Metric] increased by [Z%] (p=0.02)
**Decision:** Ship to 100% of users
