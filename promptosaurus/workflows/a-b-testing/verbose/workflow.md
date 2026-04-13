---
name: a-b-testing
description: "Structured experimentation process for data-driven decisions"
agent: "product"
category: "product"
related_workflows:
  - analytics-setup-workflow
  - feature-launch-checklist
---

# A/B Testing Workflow - Comprehensive Guide

## Overview

A/B testing (split testing) is a scientific method for comparing two or more versions of a product experience to determine which performs better. This workflow provides a systematic approach to hypothesis formation, experiment design, execution, analysis, and decision-making. Effective A/B testing enables data-driven product development, reduces risk, and maximizes the impact of product changes.

## Prerequisites

### Team and Stakeholders
- Product managers
- Data scientists/analysts
- UX designers
- Engineers (frontend/backend)
- QA team
- Marketing team (for growth experiments)
- Business stakeholders

### Technical Infrastructure
- Experimentation platform (Optimizely, LaunchDarkly, Split.io)
- Analytics infrastructure (see analytics-setup-workflow)
- Feature flag system
- Statistical analysis tools (R, Python, or built-in platform tools)
- Sample size calculators
- Reporting dashboards

### Required Preparations
- Baseline metrics established
- Success metrics defined
- Statistical power requirements understood
- Testing culture established
- Decision framework agreed upon

## Step-by-Step Process

### Phase 1: Hypothesis Development

#### Step 1: Identify Opportunity
**Opportunity Sources:**
- User research insights
- Analytics data patterns
- Customer feedback
- Competitive analysis
- Conversion funnel drop-offs
- Support ticket themes

**Opportunity Assessment:**
```
Opportunity: High cart abandonment rate (68%)
Current State: Multi-page checkout process
Potential: Industry average is 45% abandonment
Hypothesis Area: Simplifying checkout flow
Expected Impact: 10-15% reduction in abandonment
```

#### Step 2: Form Hypothesis
**Hypothesis Structure:**
```
If we [make this change]
For [this user segment]
Then we will see [this outcome]
Because [underlying reason]
```

**Example Hypotheses:**
```
Primary Hypothesis:
If we change from a 3-step to single-page checkout
For all users
Then we will see a 15% increase in checkout completion
Because users will have less opportunity to abandon

Secondary Hypothesis:
If we add progress indicators to the checkout
For mobile users
Then we will see a 10% increase in completion
Because users will understand how much is left
```

#### Step 3: Define Success Metrics
**Primary Metrics:**
- The main metric that determines success
- Directly tied to hypothesis
- Must be measurable and significant

**Secondary Metrics:**
- Supporting indicators
- Help explain primary metric changes
- Provide additional context

**Guardrail Metrics:**
- Metrics that shouldn't get worse
- Protect against unintended consequences
- Examples: revenue, user satisfaction, page load time

**Metric Definition Example:**
```yaml
primary_metric:
  name: "Checkout Completion Rate"
  definition: "Completed purchases / Checkout starts"
  current_value: 0.32
  target_improvement: 0.15
  minimum_detectable_effect: 0.05

secondary_metrics:
  - name: "Average Order Value"
    definition: "Total revenue / Number of orders"
  - name: "Time to Complete Checkout"
    definition: "Median seconds from start to completion"

guardrail_metrics:
  - name: "Cart Abandonment Rate"
    threshold: "Should not increase"
  - name: "Payment Errors"
    threshold: "Should not exceed 2%"
```

### Phase 2: Experiment Design

#### Step 4: Calculate Sample Size
**Statistical Parameters:**
- **Significance Level (α):** Typically 0.05 (5% false positive rate)
- **Power (1-β):** Typically 0.80 (80% chance of detecting effect)
- **Minimum Detectable Effect (MDE):** Smallest meaningful change
- **Baseline Conversion Rate:** Current metric value

**Sample Size Formula:**
```python
import math
from scipy import stats

def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """
    Calculate required sample size per variant
    """
    # Effect size
    effect_size = mde / math.sqrt(baseline_rate * (1 - baseline_rate))
    
    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_power = stats.norm.ppf(power)
    
    # Sample size per variant
    n = 2 * ((z_alpha + z_power) / effect_size) ** 2
    
    return math.ceil(n)

# Example calculation
baseline = 0.32  # 32% conversion rate
mde = 0.05       # 5% absolute increase
required_sample = calculate_sample_size(baseline, mde)
print(f"Required sample per variant: {required_sample}")
```

**Duration Estimation:**
```
Daily Traffic: 10,000 visitors
Required Sample: 3,000 per variant (6,000 total)
Estimated Duration: 6,000 / 10,000 = 0.6 days minimum
Recommended Duration: 7 days (full week cycle)
```

#### Step 5: Design Variations
**Variation Principles:**
- Change one variable at a time (for clarity)
- Make changes noticeable enough to impact behavior
- Ensure variations are technically feasible
- Consider edge cases and error states

**Variation Documentation:**
```markdown
## Control (A)
- Current 3-step checkout
- Shipping → Payment → Review
- Mobile: Same as desktop

## Variant (B)
- Single-page checkout
- All fields visible
- Progressive disclosure for sections
- Mobile: Accordion layout

## Key Differences
- Number of page loads: 3 vs 1
- Field visibility: Progressive vs All
- Progress indication: Steps vs Sections
```

#### Step 6: Determine Test Parameters
**Traffic Allocation:**
```yaml
test_name: "Checkout Optimization v1"
traffic_split:
  control: 50%
  variant: 50%
  
eligibility_criteria:
  - user_type: "all"
  - device: ["desktop", "mobile", "tablet"]
  - geography: "US only"  # Start with single market
  - excluded_users: ["employees", "beta_testers"]

randomization:
  method: "deterministic"  # Consistent experience per user
  seed: "user_id"
  
test_duration:
  minimum: 7 days
  maximum: 30 days
  early_stop_criteria: "harm only"  # Only stop if causing harm
```

### Phase 3: Implementation

#### Step 7: Technical Setup
**Feature Flag Implementation:**
```javascript
// Feature flag setup
const experimentConfig = {
  name: 'checkout_optimization_v1',
  variants: {
    control: {
      weight: 50,
      config: {
        checkoutType: 'multi_step',
        showProgress: true,
        stepsCount: 3
      }
    },
    treatment: {
      weight: 50,
      config: {
        checkoutType: 'single_page',
        showProgress: false,
        useAccordion: true
      }
    }
  }
};

// Assignment logic
function getVariant(userId) {
  // Check if user already assigned
  const existingAssignment = getStoredAssignment(userId);
  if (existingAssignment) {
    return existingAssignment;
  }
  
  // Random assignment based on user ID hash
  const hash = hashUserId(userId);
  const variant = hash % 100 < 50 ? 'control' : 'treatment';
  
  // Store assignment
  storeAssignment(userId, variant);
  
  // Track exposure
  analytics.track('Experiment Exposed', {
    experiment_name: 'checkout_optimization_v1',
    variant: variant,
    user_id: userId
  });
  
  return variant;
}
```

**Tracking Implementation:**
```javascript
// Track experiment metrics
function trackCheckoutMetrics(variant) {
  // Track funnel events
  analytics.track('Checkout Started', {
    experiment: 'checkout_optimization_v1',
    variant: variant,
    timestamp: Date.now()
  });
  
  // Track micro-conversions
  analytics.track('Checkout Step Completed', {
    experiment: 'checkout_optimization_v1',
    variant: variant,
    step_name: currentStep,
    time_on_step: timeSpent
  });
  
  // Track completion
  analytics.track('Purchase Completed', {
    experiment: 'checkout_optimization_v1',
    variant: variant,
    order_value: orderTotal,
    items_count: itemCount
  });
}
```

#### Step 8: Quality Assurance
**QA Checklist:**
- [ ] Both variations render correctly
- [ ] Random assignment works properly
- [ ] Users stay in same variant (sticky sessions)
- [ ] Tracking fires for all events
- [ ] Edge cases handled (errors, timeouts)
- [ ] Mobile experience tested
- [ ] No performance degradation
- [ ] Rollback plan tested

**Testing Procedures:**
```bash
# Force variant for testing
curl -X GET "https://api.example.com/checkout" \
  -H "X-Force-Variant: treatment" \
  -H "User-Id: test_user_123"

# Verify assignment distribution
SELECT 
  variant,
  COUNT(DISTINCT user_id) as users,
  COUNT(DISTINCT user_id) * 100.0 / SUM(COUNT(DISTINCT user_id)) OVER() as percentage
FROM experiment_assignments
WHERE experiment_name = 'checkout_optimization_v1'
GROUP BY variant;
```

#### Step 9: Launch Experiment
**Launch Checklist:**
- [ ] Stakeholders notified
- [ ] Documentation complete
- [ ] Monitoring dashboards ready
- [ ] Support team briefed
- [ ] Rollback plan confirmed
- [ ] Success criteria documented

**Gradual Rollout:**
```yaml
rollout_plan:
  day_1:
    traffic: 10%
    duration: 4 hours
    checkpoint: "Verify no errors"
    
  day_2:
    traffic: 25%
    duration: 24 hours
    checkpoint: "Check early metrics"
    
  day_3_onwards:
    traffic: 50%
    duration: "Until significance"
    checkpoint: "Daily monitoring"
```

### Phase 4: Monitoring and Analysis

#### Step 10: Monitor Experiment Health
**Real-time Monitoring:**
```sql
-- Sample Ratio Mismatch (SRM) check
WITH variant_counts AS (
  SELECT 
    variant,
    COUNT(DISTINCT user_id) as actual_count,
    COUNT(DISTINCT user_id) * 100.0 / SUM(COUNT(DISTINCT user_id)) OVER() as actual_percentage
  FROM experiment_exposures
  WHERE experiment_name = 'checkout_optimization_v1'
    AND exposure_date >= CURRENT_DATE
  GROUP BY variant
)
SELECT 
  variant,
  actual_count,
  actual_percentage,
  50.0 as expected_percentage,
  ABS(actual_percentage - 50.0) as deviation
FROM variant_counts;

-- Check for data quality issues
SELECT 
  DATE(exposure_time) as date,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(*) as total_exposures,
  COUNT(DISTINCT session_id) as sessions,
  SUM(CASE WHEN variant IS NULL THEN 1 ELSE 0 END) as null_variants
FROM experiment_exposures
WHERE experiment_name = 'checkout_optimization_v1'
GROUP BY date
ORDER BY date DESC;
```

**Alert Configuration:**
```yaml
alerts:
  - name: "SRM Detection"
    condition: "variant_split_deviation > 2%"
    action: "Pause experiment and investigate"
    
  - name: "Metric Degradation"
    condition: "conversion_rate_drop > 10%"
    action: "Review with team, consider stopping"
    
  - name: "Technical Errors"
    condition: "error_rate > 5%"
    action: "Immediate rollback"
```

#### Step 11: Statistical Analysis
**Interim Analysis:**
```python
import numpy as np
from scipy import stats

def analyze_experiment(control_data, treatment_data):
    """
    Perform statistical analysis on experiment results
    """
    # Calculate conversion rates
    control_rate = control_data['conversions'] / control_data['visitors']
    treatment_rate = treatment_data['conversions'] / treatment_data['visitors']
    
    # Calculate lift
    absolute_lift = treatment_rate - control_rate
    relative_lift = absolute_lift / control_rate
    
    # Perform chi-square test
    contingency_table = np.array([
        [control_data['conversions'], control_data['visitors'] - control_data['conversions']],
        [treatment_data['conversions'], treatment_data['visitors'] - treatment_data['conversions']]
    ])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    # Calculate confidence interval
    se_diff = np.sqrt(
        control_rate * (1 - control_rate) / control_data['visitors'] +
        treatment_rate * (1 - treatment_rate) / treatment_data['visitors']
    )
    ci_lower = absolute_lift - 1.96 * se_diff
    ci_upper = absolute_lift + 1.96 * se_diff
    
    return {
        'control_rate': control_rate,
        'treatment_rate': treatment_rate,
        'absolute_lift': absolute_lift,
        'relative_lift': relative_lift,
        'p_value': p_value,
        'confidence_interval': (ci_lower, ci_upper),
        'significant': p_value < 0.05
    }
```

**Sequential Testing (Optional):**
```python
# Use sequential testing to allow for early stopping
# while maintaining statistical validity

from statsmodels.stats.sequential import Sequential

# Configure sequential test
sequential_test = Sequential(
    alpha=0.05,  # Type I error rate
    beta=0.20,   # Type II error rate
    delta=0.05,  # Minimum detectable effect
    method='obrien_fleming'  # Spending function
)

# Check at each interim analysis
for day in range(1, max_days):
    result = sequential_test.test(
        successes_control=daily_conversions_control[day],
        trials_control=daily_visitors_control[day],
        successes_treatment=daily_conversions_treatment[day],
        trials_treatment=daily_visitors_treatment[day]
    )
    
    if result == 'reject':
        print(f"Significant result on day {day}")
        break
    elif result == 'accept':
        print(f"No effect detected, stop test on day {day}")
        break
```

#### Step 12: Segment Analysis
**Segmentation Dimensions:**
```sql
-- Analyze by user segment
SELECT 
  u.user_segment,
  e.variant,
  COUNT(DISTINCT e.user_id) as users,
  SUM(c.converted) as conversions,
  SUM(c.converted) * 100.0 / COUNT(DISTINCT e.user_id) as conversion_rate
FROM experiment_exposures e
JOIN users u ON e.user_id = u.user_id
LEFT JOIN conversions c ON e.user_id = c.user_id 
  AND c.timestamp >= e.exposure_time
WHERE e.experiment_name = 'checkout_optimization_v1'
GROUP BY u.user_segment, e.variant
ORDER BY u.user_segment, e.variant;

-- Analyze by device type
SELECT 
  device_type,
  variant,
  COUNT(DISTINCT user_id) as users,
  AVG(conversion_rate) as avg_conversion_rate,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY session_duration) as median_duration
FROM experiment_metrics
WHERE experiment_name = 'checkout_optimization_v1'
GROUP BY device_type, variant;
```

### Phase 5: Decision and Rollout

#### Step 13: Make Decision
**Decision Framework:**
```
Statistical Significance: p < 0.05
Practical Significance: Lift > MDE
Guardrails: All passing
Segment Analysis: No concerning segments
Qualitative Feedback: Positive or neutral

Decision Matrix:
- Ship: All criteria met
- Iterate: Some criteria met, fixable issues
- Abandon: Criteria not met or negative impact
```

**Decision Documentation:**
```markdown
## Experiment: Checkout Optimization v1

### Results Summary
- **Duration:** 14 days
- **Sample Size:** 12,000 users (6,000 per variant)
- **Primary Metric:** Checkout completion rate
  - Control: 32.0%
  - Treatment: 36.5%
  - Relative Lift: +14.1%
  - P-value: 0.002
  - 95% CI: [2.1%, 6.9%]

### Secondary Metrics
- Average Order Value: No significant change
- Time to Complete: -45 seconds (significant)
- Cart Abandonment: -4.5pp (significant)

### Guardrails
- Payment Errors: 1.8% (within threshold)
- Page Load Time: +200ms (acceptable)

### Segment Analysis
- Mobile: +18% lift (stronger effect)
- Desktop: +11% lift
- New Users: +20% lift
- Returning Users: +8% lift

### Decision: SHIP TO 100%

### Rationale
- Statistically and practically significant
- Positive across all segments
- Guardrails maintained
- Especially beneficial for mobile users
```

#### Step 14: Plan Rollout
**Rollout Strategy:**
```yaml
rollout_strategy:
  phase_1:
    name: "Gradual Rollout"
    week_1: 60%
    week_2: 80%
    week_3: 100%
    monitoring: "Daily dashboards"
    
  phase_2:
    name: "Feature Cleanup"
    remove_control: "After 30 days"
    archive_data: "After 90 days"
    
  communication:
    internal:
      - engineering: "Technical implementation"
      - support: "User guide updates"
      - sales: "Feature talking points"
    external:
      - users: "In-app notification"
      - blog: "Improvement announcement"
```

#### Step 15: Post-Experiment Analysis
**Learning Documentation:**
```markdown
## Experiment Learnings

### What Worked
- Single-page checkout reduced cognitive load
- Mobile users especially benefited
- Progressive disclosure maintained clarity

### What Didn't Work
- Some users confused by all fields visible
- Slight increase in page load time

### Surprises
- New users adapted better than expected
- Time savings larger than anticipated

### Follow-up Experiments
1. Test progress indicators in single-page
2. Optimize load time with lazy loading
3. Test autofill optimizations

### Process Improvements
- Need better mobile testing setup
- Should track more micro-conversions
- Consider longer test duration for seasonality
```

## Advanced Topics

### Multi-Variate Testing (MVT)
**When to Use:**
- Testing multiple elements simultaneously
- Understanding interaction effects
- Sufficient traffic volume

**Design Considerations:**
```
Factors:
  A: Button Color (Red, Blue)
  B: Button Text ("Buy Now", "Add to Cart")
  C: Button Position (Top, Bottom)

Full Factorial: 2 × 2 × 2 = 8 variants
Required Sample: 8 × base_sample_size
```

### Bandit Algorithms
**Multi-Armed Bandits:**
- Dynamically allocate traffic to winning variant
- Balance exploration and exploitation
- Useful for continuous optimization

```python
class ThompsonSampling:
    def __init__(self, n_variants):
        self.successes = np.zeros(n_variants)
        self.failures = np.zeros(n_variants)
    
    def select_variant(self):
        # Sample from beta distributions
        samples = [
            np.random.beta(self.successes[i] + 1, self.failures[i] + 1)
            for i in range(len(self.successes))
        ]
        return np.argmax(samples)
    
    def update(self, variant, reward):
        if reward:
            self.successes[variant] += 1
        else:
            self.failures[variant] += 1
```

### Network Effects and Interference
**Considerations:**
- Social features may have spillover effects
- Marketplace experiments affect both sides
- Geographic clustering may be needed

## Best Practices

### Experimentation Culture
- Test everything testable
- Fail fast and learn
- Document all experiments
- Share learnings broadly
- Celebrate learning, not just wins

### Statistical Rigor
- Don't peek at results early
- Run tests to completion
- Correct for multiple comparisons
- Consider practical significance
- Account for seasonality

### Technical Excellence
- Ensure clean randomization
- Monitor for SRM
- Track all relevant metrics
- Build reusable components
- Maintain experiment registry

## Common Pitfalls

### Pitfall 1: Peeking Problem
**Problem:** Checking results repeatedly inflates false positive rate
**Mitigation:** Use sequential testing or wait for completion

### Pitfall 2: Underpowered Tests
**Problem:** Test ends without detecting real effects
**Mitigation:** Calculate required sample size, ensure sufficient traffic

### Pitfall 3: Selection Bias
**Problem:** Non-random assignment corrupts results
**Mitigation:** Use proper randomization, check for SRM

### Pitfall 4: Simpson's Paradox
**Problem:** Aggregate results hide segment-level effects
**Mitigation:** Always perform segment analysis

## Success Metrics

### Experimentation Program Metrics
- Experiments run per quarter
- Percentage of decisions test-driven
- Win rate (successful experiments)
- Velocity (time from idea to decision)
- Coverage (% of surfaces testable)

### Business Impact
- Cumulative lift from experiments
- Revenue impact
- Cost savings from avoided bad changes
- Learning value generated
- Risk mitigation

## Templates and Tools

### Experiment Brief Template
```markdown
# Experiment Brief: [Name]

## Hypothesis
If we [change], then [metric] will [improve] because [reason]

## Success Metrics
- Primary: [Metric, current value, target]
- Secondary: [List metrics]
- Guardrails: [List metrics and thresholds]

## Test Design
- Control: [Description]
- Treatment: [Description]
- Traffic: [Percentage per variant]
- Duration: [Estimated days]
- Sample Size: [Required per variant]

## Analysis Plan
- Primary analysis: [Method]
- Segments: [List segments]
- Decision criteria: [Framework]
```

### Post-Experiment Report
```markdown
# Experiment Report: [Name]

## Executive Summary
[One paragraph summary of results and decision]

## Results
### Primary Metric
[Table with results]

### Secondary Metrics
[Table with results]

### Statistical Analysis
- P-value: [Value]
- Confidence Interval: [Range]
- Power Achieved: [Percentage]

## Decision
[Ship/Iterate/Abandon] because [rationale]

## Learnings
[Key insights for future experiments]

## Next Steps
[Action items and timeline]
```

## Related Resources

- **Agent Reference:** PHASE3-AGENT-003 (Product Manager)
- **Related Workflows:** analytics-setup-workflow, feature-launch-checklist
- **Statistical Tools:** R, Python (scipy, statsmodels)
- **Platforms:** Optimizely, LaunchDarkly, Amplitude Experiment
- **Reading:** "Trustworthy Online Controlled Experiments" by Kohavi et al.

## Conclusion

A/B testing is a powerful tool for making data-driven product decisions. This comprehensive workflow provides the structure needed to run valid experiments while maintaining flexibility for various testing scenarios. Remember that experimentation is not just about statistical significance but about learning what drives user behavior and business value. Build a culture of experimentation, maintain rigorous standards, and let data inform but not replace product judgment.
