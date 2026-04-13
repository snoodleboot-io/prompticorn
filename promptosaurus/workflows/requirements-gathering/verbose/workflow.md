---
name: requirements-gathering
description: "Structured approach to collect and validate product requirements"
agent: "product"
category: "product"
related_workflows:
  - feature-prioritization-workflow
  - roadmap-planning-workflow
---

# Requirements Gathering Workflow - Comprehensive Guide

## Overview

Requirements gathering is the foundation of successful product development. This workflow provides a systematic approach to collect, validate, document, and prioritize product requirements from all stakeholders. Poor requirements are the leading cause of project failure - this process ensures requirements are clear, complete, and aligned with business objectives.

## Prerequisites

### Stakeholders
- Product owner/manager
- End users or customer representatives
- Engineering team leads
- Design/UX team
- Sales and customer success teams
- Legal and compliance (if applicable)
- Executive sponsors

### Tools & Resources
- User research tools (surveys, interview platforms)
- Analytics platforms for data analysis
- Documentation tools (Confluence, Notion, etc.)
- Prototyping tools for validation
- Project management tools for tracking

### Required Inputs
- Business objectives and constraints
- Market research and competitive analysis
- Historical user feedback and support tickets
- Technical constraints and capabilities
- Budget and timeline parameters

## Step-by-Step Process

### Phase 1: Preparation and Planning

#### Step 1: Define Scope and Objectives
- Establish clear boundaries for the requirements gathering effort
- Define what success looks like for this initiative
- Set timeline and resource allocation
- Identify key decision makers and approval process

#### Step 2: Stakeholder Mapping
- Create comprehensive stakeholder list
- Categorize by influence and interest (RACI matrix)
- Define engagement strategy for each group
- Schedule initial kickoff meetings

#### Step 3: Research Current State
- Review existing documentation and requirements
- Analyze current product analytics and usage data
- Review support tickets and user feedback
- Conduct competitive analysis
- Document assumptions and constraints

### Phase 2: Requirements Discovery

#### Step 4: User Research
**Interviews:**
- Prepare interview guide with open-ended questions
- Conduct 8-12 user interviews per segment
- Focus on problems, not solutions
- Record and transcribe sessions
- Use Jobs to Be Done framework

**Surveys:**
- Design surveys for quantitative validation
- Target 100+ responses for statistical significance
- Include both closed and open-ended questions
- Segment by user type and use case

**Observation:**
- Shadow users in their natural environment
- Document current workflows and pain points
- Identify workarounds and unofficial processes
- Note emotional responses and frustrations

#### Step 5: Internal Stakeholder Sessions
- Conduct workshops with internal teams
- Gather business requirements and constraints
- Understand technical limitations and opportunities
- Align on success metrics and KPIs
- Document interdependencies

#### Step 6: Data Analysis
- Analyze usage analytics for behavior patterns
- Review conversion funnels for drop-off points
- Examine support ticket themes
- Benchmark against industry standards
- Identify gaps between current and desired state

### Phase 3: Requirements Documentation

#### Step 7: Synthesis and Categorization
- Group requirements by theme or feature area
- Identify patterns across different sources
- Separate functional from non-functional requirements
- Flag conflicting requirements for resolution
- Create requirement traceability matrix

#### Step 8: Write User Stories
**Format:** As a [user type], I want [functionality], so that [benefit]

**Components:**
- Clear user role identification
- Specific desired functionality
- Explicit business value
- Acceptance criteria using Given/When/Then format
- Definition of done

**INVEST Criteria:**
- **Independent:** Can be developed separately
- **Negotiable:** Open to discussion and refinement
- **Valuable:** Delivers clear user or business value
- **Estimable:** Can be sized by development team
- **Small:** Fits within a single iteration
- **Testable:** Has clear pass/fail criteria

#### Step 9: Define Acceptance Criteria
- Use behavior-driven development (BDD) format
- Include positive and negative test cases
- Specify edge cases and error handling
- Define performance requirements
- Include accessibility and compliance needs

### Phase 4: Validation and Prioritization

#### Step 10: Technical Feasibility Review
- Review with engineering team
- Identify technical dependencies
- Assess implementation complexity
- Estimate level of effort
- Flag technical risks and mitigation strategies

#### Step 11: Business Value Assessment
- Calculate potential ROI
- Assess strategic alignment
- Evaluate market impact
- Consider competitive advantage
- Review regulatory requirements

#### Step 12: Prioritization Workshop
**MoSCoW Method:**
- **Must Have:** Critical for launch
- **Should Have:** Important but not critical
- **Could Have:** Nice to have if time permits
- **Won't Have:** Out of scope for this release

**RICE Scoring:**
- Reach × Impact × Confidence ÷ Effort
- Document scoring rationale
- Create prioritized backlog

### Phase 5: Review and Approval

#### Step 13: Stakeholder Review Sessions
- Present requirements to each stakeholder group
- Gather feedback and concerns
- Resolve conflicts and contradictions
- Update requirements based on feedback
- Document decision rationale

#### Step 14: Final Documentation
- Create comprehensive requirements document
- Include visual mockups or wireframes
- Add process flows and user journeys
- Document assumptions and dependencies
- Create executive summary

#### Step 15: Sign-off and Baseline
- Obtain formal approval from stakeholders
- Establish requirements baseline
- Set up change control process
- Communicate approved requirements
- Archive decision documentation

## Frameworks and Methodologies

### Jobs to Be Done (JTBD)
- Focus on outcomes users want to achieve
- Understand the "job" users hire your product for
- Identify functional, emotional, and social dimensions
- Map jobs to features and requirements

### Kano Model
- **Basic Needs:** Expected features (dissatisfiers if missing)
- **Performance Needs:** Linear satisfaction increase
- **Excitement Needs:** Delighters that exceed expectations

### User Story Mapping
- Create visual representation of user journey
- Organize stories by user activities
- Identify MVP and release boundaries
- Highlight dependencies and gaps

## Best Practices

### Communication
- Use clear, unambiguous language
- Avoid technical jargon with business stakeholders
- Provide visual aids and examples
- Maintain regular stakeholder updates
- Document all decisions and changes

### Quality Assurance
- Each requirement should be:
  - Clear and unambiguous
  - Complete and consistent
  - Traceable to source
  - Testable and measurable
  - Achievable within constraints

### Stakeholder Management
- Set clear expectations early
- Manage scope creep proactively
- Address conflicts promptly
- Keep stakeholders engaged throughout
- Celebrate milestones and progress

## Common Pitfalls and Mitigation

### Pitfall 1: Requirements Creep
**Problem:** Continuous addition of new requirements
**Mitigation:** Establish clear change control process, document impact of changes

### Pitfall 2: Ambiguous Requirements
**Problem:** Vague or unclear requirements lead to rework
**Mitigation:** Use specific language, include examples, get stakeholder confirmation

### Pitfall 3: Missing Non-Functional Requirements
**Problem:** Performance, security, usability overlooked
**Mitigation:** Use checklist for NFRs, involve specialists early

### Pitfall 4: Gold Plating
**Problem:** Adding unnecessary features
**Mitigation:** Tie every requirement to user need or business objective

### Pitfall 5: Analysis Paralysis
**Problem:** Endless refinement without progress
**Mitigation:** Set time boxes, embrace iterative refinement

## Integration Points

### With Engineering
- Technical feasibility sessions
- Estimation and planning
- Architecture reviews
- Sprint planning and grooming

### With Design
- User research collaboration
- Prototype validation
- Design system constraints
- Usability testing

### With Product Strategy
- Roadmap alignment
- OKR definition
- Market positioning
- Competitive differentiation

## Success Metrics

### Process Metrics
- Requirements stability rate
- Stakeholder satisfaction scores
- Time to requirements approval
- Number of change requests

### Outcome Metrics
- Features delivered vs. planned
- User satisfaction with delivered features
- Defects traced to requirements issues
- Time to market

## Templates and Examples

### User Story Template
```
**Title:** User Registration with Email
**As a** new visitor
**I want** to register using my email address
**So that** I can save my preferences and track orders

**Acceptance Criteria:**
- GIVEN I am on the registration page
  WHEN I enter a valid email and password
  THEN I should receive a confirmation email
  
- GIVEN I enter an invalid email format
  WHEN I try to submit the form
  THEN I should see an error message
```

### Requirements Traceability Matrix
```
Req ID | Description | Source | Priority | Status | Test Cases
REQ001 | Email registration | User interviews | Must Have | Approved | TC101, TC102
REQ002 | Social login | Survey feedback | Should Have | In Review | TC103
```

## Related Resources

- **Agent Reference:** PHASE3-AGENT-003 (Product Manager)
- **Subagent:** requirements-analyst for detailed analysis
- **Next Workflows:** feature-prioritization-workflow, roadmap-planning-workflow
- **Templates:** User story templates, requirements document template
- **Tools:** JIRA, ProductBoard, Aha!, Confluence

## Conclusion

Effective requirements gathering is iterative and collaborative. This workflow provides structure while maintaining flexibility to adapt to your specific context. Remember that requirements are living documents that evolve throughout the product lifecycle. Regular validation and refinement ensure alignment with user needs and business objectives.