---
name: "Analytics Setup Workflow"
description: "Implementation guide for product analytics and measurement"
agent: "product"
category: "product"
related_workflows:
  - a-b-testing-workflow
  - feature-launch-checklist
---

# Analytics Setup Workflow

## Goal
Establish comprehensive analytics to measure product performance and user behavior.

## Quick Steps

1. **Define Key Metrics**
   - North Star metric
   - AARRR funnel metrics
   - Feature-specific KPIs

2. **Plan Tracking Schema**
   - Event taxonomy design
   - User properties definition
   - Naming conventions

3. **Implement Tracking**
   - Analytics SDK integration
   - Event instrumentation
   - QA tracking accuracy

4. **Create Dashboards**
   - Executive dashboard
   - Product team views
   - Alert configurations

5. **Document & Train**
   - Tracking documentation
   - Team training on tools

6. **Monitor & Maintain**
   - Regular data audits
   - Schema evolution process

## Key Frameworks

- **AARRR:** Acquisition, Activation, Retention, Revenue, Referral
- **North Star Metric:** Single metric reflecting core value
- **Event-Based Analytics:** Track user actions, not pageviews

## Success Factors

- Metrics tied to business objectives
- Consistent naming conventions
- Data quality validated
- Stakeholder access to dashboards
- Regular metric reviews

## Template Output

**Event Name:** user_action_completed
**Properties:** {user_id, action_type, success, duration_ms}
**Dashboard:** [Link to metrics dashboard]
