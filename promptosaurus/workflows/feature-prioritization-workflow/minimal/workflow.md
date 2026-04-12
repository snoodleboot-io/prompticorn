---
name: "Feature Prioritization Workflow"
description: "Data-driven process to prioritize features based on value and effort"
agent: "product"
category: "product"
related_workflows:
  - requirements-gathering-workflow
  - roadmap-planning-workflow
---

# Feature Prioritization Workflow

## Goal
Objectively prioritize features to maximize value delivery with available resources.

## Quick Steps

1. **List All Features**
   - Backlog review, new requests
   - Technical debt items

2. **Score Each Feature**
   - Apply RICE framework
   - Calculate priority score

3. **Assess Dependencies**
   - Technical prerequisites
   - Resource constraints

4. **Stack Rank Features**
   - Sort by score and dependencies
   - Consider strategic alignment

5. **Validate with Stakeholders**
   - Review prioritized list
   - Adjust based on feedback

6. **Lock Sprint/Quarter Plan**
   - Commit to top priorities

## Key Frameworks

**RICE Scoring:**
- Reach: # of users affected
- Impact: Low (0.25) to Massive (3)
- Confidence: Low (50%) to High (100%)
- Effort: Person-months required
- Score = (Reach × Impact × Confidence) / Effort

## Success Factors

- Data-driven scoring, not opinions
- All stakeholders represented
- Clear rationale documented
- Regular reprioritization cycles
- Communicated effectively

## Template Output

**Priority 1:** [Feature] | RICE: [Score] | Effort: [X] weeks
**Rationale:** [Why this is top priority]
