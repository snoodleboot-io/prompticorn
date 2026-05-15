---
name: "decision-log"
languages: ["markdown"]
subagents: ["ask", "architect"]
---

# Decision Log (ADR) Workflow (Comprehensive)

## Overview

Architecture Decision Records (ADRs) document important technical and architectural decisions. They provide historical context, rationale, and consequences for future reference.

**Purpose:**
- Preserve context for decisions (why this approach was chosen)
- Help new team members understand system evolution
- Prevent revisiting settled debates
- Provide audit trail for compliance/governance

**When to write an ADR:**
- Architectural choices (database, framework, deployment model)
- Technology selection (language, library, third-party service)
- Significant design patterns or conventions
- Breaking changes to APIs or data models
- Security or compliance decisions

**When NOT to write an ADR:**
- Minor implementation details (variable naming)
- Obvious choices following established patterns
- Temporary workarounds or experiments
- Decisions easily reversed without cost

---

## Phase 1: Context Gathering

### 1.1 Identify the Decision

**Questions to answer:**
1. What exactly is being decided?
2. Who needs to make this decision?
3. When does the decision need to be made?
4. What happens if we don't decide (cost of delay)?

**Example:**
```markdown
Decision: Choose primary database for new microservice
Deciders: Engineering Lead, CTO, Senior Backend Engineers
Timeline: Decision needed by March 15 (dev starts March 20)
Cost of delay: 1 week delay = $50K in lost revenue
```

### 1.2 Understand the Problem

**Define the problem clearly:**
- What is broken or missing?
- Who is affected?
- What is the impact of not solving it?
- What constraints exist (time, budget, technical)?

**Example problem statement:**
```markdown
## Problem

Current monolithic MySQL database is reaching capacity limits:
- Query latency increased 300% over 6 months
- Write throughput capped at 5K/sec (need 20K/sec)
- Schema changes require 2-hour downtime
- No geographic distribution (all traffic routes through us-east-1)

Impact:
- Page load times degraded from 200ms to 800ms
- Peak traffic causes 5xx errors (lost sales)
- Cannot launch in EU market due to latency
```

### 1.3 Research Alternatives

**For each option, document:**
- Description (what is it?)
- How it solves the problem
- Advantages (pros)
- Disadvantages (cons)
- Effort required (time, cost, complexity)
- Risks (what could go wrong?)

**Research sources:**
- Vendor documentation
- Case studies from similar companies
- Engineering blogs
- Proof-of-concept implementations
- Team member expertise

**Minimum: 2 alternatives + "do nothing" option**

---

## Phase 2: ADR Creation

### 2.1 File Structure

**Directory structure:**
```
docs/
├── decisions/           # OR planning/current/adrs/
│   ├── ADR-001-use-postgresql.md
│   ├── ADR-002-implement-caching.md
│   ├── ADR-003-migrate-to-kubernetes.md
│   └── README.md       # Index of all ADRs
```

**Naming convention:**
```
ADR-{number}-{brief-title}.md

Examples:
ADR-001-use-postgresql-over-mongodb.md
ADR-002-implement-redis-caching.md
ADR-003-adopt-graphql-api.md
```

**Numbering:**
- Sequential (001, 002, 003...)
- Never reuse numbers (even if ADR is superseded)
- Gaps are okay (ADR-005 can exist without ADR-004)

### 2.2 ADR Template

**Complete ADR structure:**

```markdown
# ADR-{number}: {Decision Title}

**Date:** YYYY-MM-DD  
**Status:** Proposed | Accepted | Rejected | Superseded | Deprecated  
**Deciders:** {Names or roles}  
**Technical Story:** {Link to ticket/epic}

## Context

### Problem Statement
{Clear description of the problem being solved}

### Background
{Any relevant historical context, previous attempts, or related systems}

### Constraints
- **Technical:** {Technical limitations or requirements}
- **Business:** {Budget, timeline, compliance requirements}
- **Team:** {Skills, capacity, availability}

### Goals
1. {Primary goal}
2. {Secondary goal}
3. {Tertiary goal}

### Non-Goals
- {What this decision explicitly does NOT address}

---

## Decision

{Clear, unambiguous statement of what was decided}

**Example:**
We will migrate from MongoDB to PostgreSQL for our primary transactional database.

---

## Alternatives Considered

### Option 1: {Name} {✓ SELECTED | ✗ REJECTED}

**Description:**
{What is this option?}

**How it solves the problem:**
{Specific ways this addresses the problem}

**Pros:**
- {Advantage 1}
- {Advantage 2}
- {Advantage 3}

**Cons:**
- {Disadvantage 1}
- {Disadvantage 2}

**Effort:** {Low | Medium | High}  
**Cost:** {$ estimate or "Negligible"}  
**Timeline:** {How long to implement?}

**Risks:**
- {Risk 1 and mitigation}
- {Risk 2 and mitigation}

---

### Option 2: {Name} {✗ REJECTED}

{Same structure as Option 1}

---

### Option 3: Do Nothing {✗ REJECTED}

**Description:**
Continue with current approach

**Cons:**
- {Why status quo is unacceptable}

---

## Rationale

{Detailed explanation of why the selected option was chosen over alternatives}

**Key factors:**
1. {Factor 1: e.g., "Best performance for our query patterns"}
2. {Factor 2: e.g., "Team already has PostgreSQL expertise"}
3. {Factor 3: e.g., "Lower total cost of ownership"}

**Trade-offs accepted:**
- {Trade-off 1: e.g., "Higher migration effort vs MongoDB"}
- {Trade-off 2: e.g., "Less flexible schema vs document store"}

---

## Consequences

### Positive

**Immediate benefits:**
- {Benefit 1}
- {Benefit 2}

**Long-term benefits:**
- {Benefit 1}
- {Benefit 2}

### Negative

**Immediate costs:**
- {Cost 1: e.g., "3-week migration effort"}
- {Cost 2: e.g., "$5K/month higher hosting cost"}

**Technical debt created:**
- {Debt 1}
- {Debt 2}

### Neutral

**Other changes:**
- {Change 1}
- {Change 2}

---

## Implementation Plan

### Phase 1: Preparation ({Timeline})
- [ ] {Task 1}
- [ ] {Task 2}
- [ ] {Task 3}

### Phase 2: Migration ({Timeline})
- [ ] {Task 1}
- [ ] {Task 2}

### Phase 3: Validation ({Timeline})
- [ ] {Task 1}
- [ ] {Task 2}

### Rollback Plan
{How to undo this if it fails}

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| {Risk 1} | High/Med/Low | High/Med/Low | {How we'll handle it} |
| {Risk 2} | High/Med/Low | High/Med/Low | {How we'll handle it} |

---

## Success Criteria

**How we'll know this decision was correct:**
- [ ] {Measurable criterion 1: e.g., "Query latency < 100ms p95"}
- [ ] {Measurable criterion 2: e.g., "Zero downtime during migration"}
- [ ] {Measurable criterion 3: e.g., "Team onboarded in 2 weeks"}

**Measurement:**
- {How criterion 1 will be measured}
- {How criterion 2 will be measured}

---

## Related Decisions

- **Depends on:** [ADR-001: Infrastructure Provider Selection](./ADR-001-aws-vs-gcp.md)
- **Supersedes:** [ADR-005: MongoDB Schema Design](./ADR-005-mongodb-schema.md)
- **Related:** [ADR-010: Caching Strategy](./ADR-010-caching.md)

---

## Revisit / Review

**Review date:** YYYY-MM-DD (e.g., 6 months from decision)

**Triggers for re-evaluation:**
- {Event 1: e.g., "If query latency exceeds 500ms again"}
- {Event 2: e.g., "PostgreSQL licensing changes"}
- {Event 3: e.g., "New database technology emerges"}

---

## References

- {Link to technical spike}
- {Link to proof-of-concept}
- {Link to vendor documentation}
- {Link to case study or blog post}

---

## Approval

**Approved by:**
- {Name, Role} - YYYY-MM-DD
- {Name, Role} - YYYY-MM-DD

**Comments from review:**
- {Reviewer 1: Concern about migration timeline}
- {Reviewer 2: Suggested phased rollout}
```

### 2.3 Status Values

**Proposed:** Decision drafted, awaiting approval

**Accepted:** Approved and being implemented or already in use

**Rejected:** Proposed but not chosen (document why for future reference)

**Superseded:** Replaced by a newer decision (link to the new ADR)

**Deprecated:** Still in use but planned for removal (link to replacement ADR)

---

## Phase 3: Writing Best Practices

### 3.1 Clarity Principles

**Write for the future reader:**
- Assume they don't have context
- Assume they don't remember the discussion
- Assume they will question the decision

**Be specific:**
```markdown
# Bad: Vague reasoning
We chose PostgreSQL because it's better.

# Good: Specific reasoning
We chose PostgreSQL because:
1. ACID guarantees prevent inventory overselling (critical for e-commerce)
2. JSON support allows flexible product attributes
3. Team has 5 years PostgreSQL experience vs 0 MongoDB experience
4. 40% lower hosting cost vs managed MongoDB ($2K/month savings)
```

**Use data:**
```markdown
# Bad: Subjective claim
PostgreSQL is faster for our use case.

# Good: Measured data
PostgreSQL query benchmarks:
- Read-heavy workload: 2,400 QPS (MongoDB: 1,800 QPS)
- Write-heavy workload: 1,200 QPS (MongoDB: 1,500 QPS)
- Mixed workload: 1,800 QPS (MongoDB: 1,600 QPS)

Our workload is 80% reads, so PostgreSQL is 33% faster.
```

### 3.2 Conciseness

**Target length: 2-5 pages (600-1500 words)**

**Techniques:**
- Use bullet points over paragraphs
- Use tables for comparisons
- Use headings for skimmability
- Link to external docs rather than copying

**Example: Comparison table vs prose**

❌ **Bad (prose):**
```markdown
MongoDB is a document database that stores data in JSON-like documents.
It offers flexible schemas and is good for rapid development. However,
it lacks ACID guarantees and requires manual sharding. PostgreSQL is
a relational database with ACID guarantees and SQL support. It has a
rigid schema but offers strong consistency...
```

✓ **Good (table):**
```markdown
| Feature | PostgreSQL | MongoDB |
|---------|-----------|---------|
| Data model | Relational | Document |
| Schema | Strict | Flexible |
| ACID | Yes | Limited |
| Query language | SQL | MQL |
| Scaling | Vertical + sharding | Horizontal |
| Team experience | 5 years | 0 years |
```

### 3.3 Tone

**Objective, not defensive:**
```markdown
# Bad: Defensive tone
We HAD to choose PostgreSQL because MongoDB is terrible and anyone
who disagrees doesn't understand databases.

# Good: Objective tone
We chose PostgreSQL over MongoDB based on ACID requirements and
team expertise. MongoDB remains a valid option for document-centric
workloads and may be revisited in the future.
```

**Acknowledge trade-offs:**
```markdown
# Bad: Ignoring downsides
PostgreSQL is the perfect solution with no drawbacks.

# Good: Honest trade-offs
PostgreSQL provides ACID guarantees and strong consistency, but
requires more upfront schema design and vertical scaling is more
expensive than MongoDB's horizontal sharding. We accept this
trade-off because data consistency is critical for inventory.
```

---

## Phase 4: Review and Approval

### 4.1 Stakeholder Identification

**Who needs to approve:**
- **Technical lead:** Validates technical soundness
- **Product owner:** Validates alignment with business goals
- **Security/Compliance:** For decisions affecting security or compliance
- **Finance:** For decisions with significant cost impact

**Review process:**
1. Author drafts ADR (status: Proposed)
2. Share with stakeholders for comment (1-3 days)
3. Address feedback and update ADR
4. Get explicit approval (signature, PR approval, email)
5. Change status to Accepted
6. Commit to repository

### 4.2 Common Review Questions

**Reviewers should ask:**
- Is the problem clearly stated?
- Were enough alternatives considered?
- Is the rationale convincing?
- Are risks identified and mitigated?
- Is the decision reversible if wrong?
- Are success criteria measurable?

### 4.3 Handling Disagreement

**If stakeholders disagree:**
1. Document the disagreement in the ADR
2. Escalate to decision-maker (CTO, VP Engineering)
3. Record final decision and dissenting opinions
4. Move forward with decided option

**Example:**
```markdown
## Approval

**Approved by:**
- Alice (CTO) - 2026-03-15

**Dissenting opinions:**
- Bob (Senior Engineer) prefers MongoDB for schema flexibility
- Recorded for future reference if requirements change
```

---

## Phase 5: Lifecycle Management

### 5.1 ADR Index

**Maintain a README.md in planning/current/adrs/:**

```markdown
# Architecture Decision Records

## Active Decisions

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-003](./ADR-003-kubernetes.md) | Migrate to Kubernetes | Accepted | 2026-03-15 |
| [ADR-002](./ADR-002-redis-cache.md) | Implement Redis Caching | Accepted | 2026-02-20 |
| [ADR-001](./ADR-001-postgresql.md) | Use PostgreSQL | Accepted | 2026-01-10 |

## Superseded Decisions

| ADR | Title | Status | Superseded By |
|-----|-------|--------|---------------|
| [ADR-005](./ADR-005-mongodb.md) | Use MongoDB | Superseded | [ADR-001](./ADR-001-postgresql.md) |

## Rejected Decisions

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-007](./ADR-007-nosql.md) | Adopt NoSQL | Rejected | 2026-01-08 |
```

### 5.2 Updating Existing ADRs

**When to update:**
- Status changes (Proposed → Accepted)
- Implementation plan updates
- New risks discovered
- Success criteria measured

**When NOT to update:**
- Don't change the original decision rationale
- Don't delete rejected alternatives
- Don't rewrite history

**How to supersede an ADR:**
1. Create new ADR with updated decision
2. Update old ADR status to "Superseded"
3. Add link in old ADR: "Superseded by: ADR-XXX"
4. Add link in new ADR: "Supersedes: ADR-YYY"

### 5.3 Review Cadence

**Schedule reviews:**
- Set calendar reminders for review dates
- Review during architecture meetings
- Review when triggering events occur

**Review outcomes:**
1. **Reaffirm:** Decision still correct, extend review date
2. **Modify:** Update ADR with new information
3. **Supersede:** Create new ADR replacing this one
4. **Deprecate:** Mark for removal, link to replacement

---

## Tools and Automation

### ADR Tools

**adr-tools (command line):**
```bash
# Install
npm install -g adr-log

# Create new ADR
adr new "Use PostgreSQL for primary database"

# List ADRs
adr list

# Generate website
adr generate toc > planning/current/adrs/README.md
```

**log4brains (web UI):**
```bash
# Install
npx log4brains init

# Start web UI
npx log4brains preview

# Build static site
npx log4brains build
```

### CI Integration

**Validate ADRs in CI:**
```yaml
# .github/workflows/adr-validation.yml

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check ADR format
        run: |
          # Verify all ADRs have required sections
          for file in planning/current/adrs/ADR-*.md; do
            grep -q "## Context" "$file" || echo "Missing Context: $file"
            grep -q "## Decision" "$file" || echo "Missing Decision: $file"
            grep -q "## Consequences" "$file" || echo "Missing Consequences: $file"
          done
      
      - name: Check ADR numbering
        run: |
          # Verify sequential numbering
          cd docs/decisions
          ls ADR-*.md | sort -V | awk -F'[-.]' '{print $2}' | sort -n | uniq -d
```

---

## Examples

### Example 1: Simple Decision

**ADR-012: Use Tailwind CSS for Styling**

```markdown
# ADR-012: Use Tailwind CSS for Styling

**Date:** 2026-04-10  
**Status:** Accepted  
**Deciders:** Frontend Team

## Context
Need to choose CSS framework for new admin dashboard. Requirements:
- Fast development
- Consistent design system
- Easy customization

## Decision
Use Tailwind CSS utility-first framework.

## Alternatives Considered

### Tailwind CSS ✓ SELECTED
**Pros:** Utility-first, no unused CSS, fast development
**Cons:** HTML can get verbose
**Effort:** Low (2 days setup)

### Bootstrap
**Pros:** Pre-built components, familiar to team
**Cons:** Harder to customize, larger bundle size
**Effort:** Low (2 days setup)

### Custom CSS
**Pros:** Full control
**Cons:** Slow development, inconsistent
**Effort:** High (2 weeks)

## Consequences

**Positive:**
- 50% faster component development
- Consistent design tokens
- Tree-shaking reduces bundle size

**Negative:**
- Learning curve for new developers
- Verbose HTML classes

## Review Date
2027-04-10 (1 year)
```

### Example 2: Complex Decision

See full template above for comprehensive example.

---

## Common Mistakes to Avoid

**Mistake 1: Too detailed (implementation docs instead of decision)**
```markdown
# Bad: Implementation guide
Step 1: Run `npm install postgresql`
Step 2: Configure connection pool with these settings...

# Good: Decision rationale
We chose PostgreSQL because it provides ACID guarantees critical
for our financial transactions.
```

**Mistake 2: No alternatives documented**
```markdown
# Bad: Only one option
We will use PostgreSQL.

# Good: Multiple options compared
We evaluated PostgreSQL, MongoDB, and MySQL. PostgreSQL was chosen
because... (see Alternatives section)
```

**Mistake 3: Vague consequences**
```markdown
# Bad: Vague
This will improve performance.

# Good: Specific
Query latency will decrease from 800ms to <100ms p95 based on
benchmark tests (see attached results).
```

---

## Resources

**ADR tools:**
- adr-tools: github.com/npryce/adr-tools
- log4brains: github.com/thomvaill/log4brains
- adr-viewer: github.com/mrwilson/adr-viewer

**Templates:**
- Michael Nygard's template: cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Markdown Architectural Decision Records (MADR): adr.github.io/madr/

**Examples:**
- GitHub ADRs: github.com/joelparkerhenderson/architecture-decision-record
- AWS Well-Architected: aws.amazon.com/architecture/well-architected/
