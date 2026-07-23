# Architecture Documentation (Minimal)

## Purpose
Record the structure of a system and the reasoning behind it, so that the next
engineer can change it without re-deriving every decision from scratch.

## Core Techniques

### 1. Write ADRs for Decisions, Not for Designs
An Architecture Decision Record captures one choice, its forces, and its cost.
It is immutable — you supersede it, you never edit it.

```markdown
# ADR-0014: Use Postgres advisory locks for job de-duplication

Status: Accepted (2026-03-02). Supersedes ADR-0009.

## Context
The ingest worker runs 6 replicas. Each polls `jobs` every 2s and can pick the
same row, so we saw ~40 duplicate invoice postings/day. We already run Postgres
14 for the job table; adding Redis for locks means a second store in the
critical path and a second failure mode during deploys.

## Decision
Take a session-scoped `pg_try_advisory_lock(hashtext(job_id))` inside the
existing transaction. If the lock is not acquired, skip the row.

## Consequences
+ No new infrastructure; the lock dies with the connection, so a crashed worker
  releases automatically — no TTL tuning.
- Locks are per-primary. A read-replica failover drops all held locks, so a job
  can be picked twice across a failover. We accept this: the posting endpoint is
  idempotent on `job_id`.
- Caps us at the connection pool size (currently 100) for concurrent jobs.
  Above ~80 sustained we must revisit; see "Revisit if" below.

## Revisit if
Sustained concurrent jobs exceed 80, or we introduce a second writer database.
```

The "Consequences" section is where ADRs earn their keep. If it only lists
benefits, the decision was not actually analysed.

### 2. Use C4 Levels and Know Each One's Audience
| Level | Shows | Audience | Refresh |
|---|---|---|---|
| 1 Context | Your system, users, external systems | Anyone, incl. non-technical | Rarely |
| 2 Container | Deployable units and datastores | New engineers, on-call | Per quarter |
| 3 Component | Modules inside one container | The team owning it | Only if maintained |
| 4 Code | Classes, schemas | Nobody — generate it | Never by hand |

Most teams need Level 1 and Level 2 and nothing else. Level 4 diagrams are
obsolete before the PR merges; let the IDE draw them on demand.

### 3. Generate What You Can, Hand-Draw What You Must
Diagrams rot because they duplicate a truth that lives elsewhere. Break the
duplication:
- Infrastructure topology — render from Terraform state or `cdk synth`, not by hand
- Service call graph — derive from distributed tracing or service-mesh config
- Entity relationships — generate from the live schema (see `mermaid-erd-creation`)
- Context and container diagrams — hand-authored, but as text in the repo

Keep hand-drawn diagrams as Mermaid or Structurizr DSL committed next to the
code, so they appear in diffs and can be reviewed like anything else. A PNG
dragged out of a whiteboard tool is unreviewable and will be wrong within months.

### 4. Reach for arc42 When You Need a Whole-System Document
ADRs are point decisions; arc42 is a 12-section template for the system as a
whole. In practice sections 1 (goals), 3 (scope and context), 4 (solution
strategy), 5 (building blocks), 8 (crosscutting concepts) and 11 (risks and
technical debt) carry nearly all the value. Section 9 holds the architecture
decisions — link out to your ADRs rather than duplicating them.

### 5. Document Constraints and Quality Attributes Numerically
"Must be scalable" is unfalsifiable and therefore unusable. "Must sustain 3k
writes/sec at p99 < 150 ms with 400 GB of hot data" constrains the design and
can be tested. Every quality attribute needs a number and a measurement method.

## Warning Signs

- ADRs whose Consequences list only upsides, or that were edited after acceptance
- Diagrams with no author, no date, and no way to regenerate them
- Component-level diagrams maintained by hand while Context is missing entirely
- A wiki page titled "Architecture" last touched before the current stack landed
- Requirements phrased as "fast", "scalable", "secure" with no threshold
- Decisions discoverable only in Slack scrollback or a closed PR thread
- New engineers asking questions the docs claim to answer
