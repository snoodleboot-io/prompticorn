---
type: subagent
agent: ask
name: decision-log
variant: verbose
version: 1.0.0
description: Record architectural and technical decisions with detailed examples
mode: subagent
tools: [write]
workflows:
  - decision-log-workflow
---

# Decision Log (Verbose)

Architecture Decision Records (ADRs) document important technical and architectural decisions for future reference.

---

## When to Write an ADR

**Write an ADR when:**
- Decision affects multiple systems or teams
- Trade-offs were considered (not obvious)
- Decision is hard to reverse
- Future maintainers need context

**Don't write an ADR for:**
- Following established patterns
- Trivial implementation details
- Obvious technical choices

---

## Information Gathering

### Questions to Ask

If context is incomplete, ask:

1. **What decision is being made?**
   - Be specific: "Use PostgreSQL" not "database choice"

2. **What problem does it solve?**
   - What's broken or missing?
   - What happens if we don't decide?

3. **What alternatives were considered?**
   - List 2-4 realistic options
   - Include "do nothing" if applicable

4. **Why was this option chosen?**
   - What tipped the scales?
   - What criteria mattered most?

5. **What are the risks and trade-offs?**
   - What could go wrong?
   - What did we give up?

---

## ADR Format

### Template

```markdown
# ADR-[number]: [Title in Title Case]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Rejected | Superseded by ADR-XXX
**Deciders:** [Names or team names]

## Context

Why is this decision being made now?
What is the problem or opportunity?
What constraints or requirements exist?

## Decision

Clear statement of what was decided.
Use active voice: "We will use PostgreSQL for primary database."

## Alternatives Considered

### Option 1: [Name]
**Approach:** [Brief description]
**Pros:**
- [Advantage 1]
- [Advantage 2]
**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]
**Decision:** Accepted | Rejected | Deferred

### Option 2: [Name]
[Same structure as Option 1]

### Option 3: [Name]
[Same structure as Option 1]

## Rationale

Why did we choose the selected option?
What factors were most important?
What evidence supported this choice?

## Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative / Trade-offs:**
- [What we're giving up]
- [New complexity introduced]

**Risks:**
- [What could go wrong]
- [Mitigation strategies]

## Implementation Plan (optional)

High-level steps to implement this decision.

## Review Date

When should we revisit this decision?
Under what conditions should we reconsider?
```

---

## Complete Example

```markdown
# ADR-003: Use PostgreSQL for Primary Database

**Date:** 2026-04-10
**Status:** Accepted
**Deciders:** Engineering Team (Alice, Bob, Carol)

## Context

Our application currently stores data in SQLite files. We're experiencing:
- Concurrent write conflicts (SQLite doesn't handle this well)
- Growing data size (approaching SQLite's practical limits)
- Need for full-text search and JSON querying
- Team familiarity with SQL but no experience with NoSQL

We need a production-ready database that handles:
- 1000+ concurrent users
- 100GB+ data within 2 years
- Complex queries with joins
- ACID guarantees for financial transactions

## Decision

We will use PostgreSQL 15+ as our primary application database.

## Alternatives Considered

### Option 1: PostgreSQL
**Approach:** Relational database with strong ACID guarantees
**Pros:**
- Industry standard with 30+ years of stability
- Excellent documentation and community support
- Built-in full-text search and JSON support
- Strong consistency guarantees (critical for financial data)
- Team has SQL experience
- Free and open source

**Cons:**
- Requires separate deployment/management
- Vertical scaling has limits (but we're years away from this)
- More complex than SQLite for local development

**Decision:** ✅ Accepted

### Option 2: MongoDB
**Approach:** NoSQL document database
**Pros:**
- Flexible schema (easy to iterate)
- Horizontal scaling built-in
- Good for semi-structured data

**Cons:**
- Team has no MongoDB experience (learning curve)
- Weaker consistency guarantees by default
- JSON documents don't fit our relational data model
- More expensive to run at scale

**Decision:** ❌ Rejected - Data is relational, team lacks NoSQL experience

### Option 3: MySQL/MariaDB
**Approach:** Alternative relational database
**Pros:**
- Similar to PostgreSQL (relational, SQL)
- Wide adoption
- Good performance

**Cons:**
- Weaker full-text search than PostgreSQL
- Less robust JSON support
- Licensing concerns with MySQL (Oracle owned)
- Team prefers PostgreSQL ecosystem

**Decision:** ❌ Rejected - PostgreSQL offers better feature fit

### Option 4: Stay with SQLite
**Approach:** Keep current database
**Pros:**
- No migration needed
- Simple deployment (single file)
- Good for development

**Cons:**
- Doesn't solve concurrent write problem
- Not suitable for production at our scale
- No horizontal scaling path

**Decision:** ❌ Rejected - Doesn't meet production requirements

## Rationale

PostgreSQL was chosen because:

1. **Data Model Fit:** Our data is highly relational (users, orders, payments). PostgreSQL excels at this.

2. **Team Experience:** Team knows SQL but not NoSQL. Learning curve is minimal.

3. **Feature Requirements:**
   - ACID guarantees needed for financial transactions ✓
   - Full-text search for product catalog ✓
   - JSON columns for flexible metadata ✓
   - Complex queries with joins ✓

4. **Scalability:** PostgreSQL handles our 2-year growth plan (100GB, 1000 concurrent users) easily.

5. **Ecosystem:** Rich tooling (pgAdmin, Postico), ORMs (SQLAlchemy), and hosting options (AWS RDS, Supabase).

6. **Cost:** Open source, no licensing fees. Lower operational cost than managed MongoDB.

## Consequences

**Positive:**
- Strong data consistency guarantees
- Industry-standard tooling and ecosystem
- Team can leverage existing SQL knowledge
- Clear path to production scale

**Negative / Trade-offs:**
- Need to manage a separate database server (vs SQLite's single file)
- Local development requires Docker or PostgreSQL install
- Vertical scaling limits (though distant concern)
- Schema migrations more formal than NoSQL

**Risks:**
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database becomes bottleneck | Low | High | Use read replicas, caching (Redis), and query optimization |
| Team struggles with PostgreSQL | Low | Medium | Training sessions, pair programming, extensive documentation |
| Migration from SQLite introduces bugs | Medium | Medium | Thorough testing on staging with production-size data |

## Implementation Plan

1. **Week 1:** Set up PostgreSQL on staging environment
2. **Week 2:** Migrate schema from SQLite to PostgreSQL
3. **Week 3:** Write and test data migration scripts
4. **Week 4:** Migrate development environments to PostgreSQL
5. **Week 5:** Production migration (with rollback plan)

## Review Date

**Review in 12 months (April 2027)** or if:
- Data grows beyond 500GB (approaching PostgreSQL single-server limits)
- Concurrent users exceed 5000 (may need read replicas)
- Team composition changes significantly (e.g., NoSQL experts join)
```

---

## Writing Guidelines

### ✅ Good ADRs

**Characteristics:**
- Readable in 3 minutes
- Written for future maintainer (not in the room)
- Specific, not vague ("Use PostgreSQL 15+" not "use a database")
- Documents rationale, not just decision
- Honest about trade-offs

### ❌ Bad ADRs

**Anti-patterns:**
- Too long (> 2 pages)
- Missing alternatives
- No rationale ("because I said so")
- Ignoring trade-offs
- Obvious decisions documented

---

## ADR Statuses

| Status | Meaning |
|--------|---------|
| **Proposed** | Decision under discussion, not yet final |
| **Accepted** | Decision made and approved |
| **Rejected** | Proposal considered but not chosen |
| **Superseded** | Replaced by newer ADR (link to replacement) |
| **Deprecated** | No longer recommended, but not replaced |

---

## Storage and Naming

**Location:** 
- Planning (active): `planning/current/adrs/`
- Planning (complete): `planning/complete/adrs/`
- Documentation (finalized): `docs/decisions/`

**Filename format:** `ADR-NNN-title-in-kebab-case.md`

**Examples:**
- `ADR-001-use-typescript-for-frontend.md`
- `ADR-002-implement-event-sourcing.md`
- `ADR-003-use-postgresql-for-primary-database.md`

**Numbering:**
- Sequential (001, 002, 003...)
- Never reuse numbers (even if ADR is rejected)
- Gaps are okay (deleted draft ADRs)

---

## Common Mistakes

### ❌ Documenting Obvious Choices

**Don't:**
```
ADR-015: Use Git for Version Control

We will use Git because everyone uses Git.
```

This is too obvious to document.

### ❌ Missing Trade-offs

**Don't:**
```
## Decision
Use microservices architecture.

## Consequences
**Positive:**
- Better scalability
- Independent deployments

**Negative:**
- None
```

There are ALWAYS trade-offs. Microservices add complexity, operational overhead, debugging difficulty, etc.

### ❌ Vague Alternatives

**Don't:**
```
## Alternatives
- Option A: Database
- Option B: Other database
```

Be specific: PostgreSQL, MongoDB, DynamoDB, etc.

### ✅ Complete Trade-off Analysis

**Do:**
```
## Consequences

**Positive:**
- Independent service deployments reduce coordination
- Teams can choose best tech for their service
- Horizontal scaling per service

**Negative:**
- Distributed system complexity (network failures, eventual consistency)
- More operational overhead (monitoring, logging across services)
- Debugging spans multiple services
- Data consistency harder to maintain

**Risks:**
- Network latency between services (mitigation: service mesh, retries)
- Shared nothing means duplicated logic (mitigation: shared libraries)
```
