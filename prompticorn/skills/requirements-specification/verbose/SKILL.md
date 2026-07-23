# Requirements Specification (Verbose)

## Core Patterns

### The Falsifiability Test

A requirement earns the name only if someone could write a check that fails.
Everything else is a preference wearing a requirement's clothes, and it will be
settled in code review by whoever argues longest.

Apply one question to each line: **what observation would prove this unmet?**

| ❌ Wish | ✅ Requirement |
|---|---|
| The system should be fast | Search returns p95 < 200 ms and p99 < 500 ms at 500 req/s sustained for 10 min, measured server-side at the API gateway, excluding client network time |
| The UI should be intuitive | 8 of 10 first-time users complete account creation unaided in under 90 s in moderated testing |
| Handle large files | Accepts CSV to 500 MB / 2,000,000 rows; larger uploads rejected with HTTP 413 and a body naming the limit |
| Must be secure | All endpoints require a valid bearer token; tokens expire in 15 min; auth failure returns 401 with no discriminating detail |
| Support many users | 10,000 concurrent authenticated sessions, error rate < 0.1%, p99 < 800 ms |
| Reports should be accurate | Ledger totals match the source system to the cent for all closed periods; any discrepancy raises an alert within 15 min |
| Errors handled gracefully | On upstream timeout (> 3 s), return 503 with `Retry-After: 30`; the user's unsaved draft survives the failure |

Words that reliably mark an unwritten requirement: *fast, scalable, intuitive,
robust, seamless, user-friendly, flexible, appropriate, as needed, if possible,
etc., and/or,* and every use of *handle*. Each conceals a number nobody has
agreed to yet. Grep for them before review.

Two subtler failures. **Solutions disguised as requirements** — "the system
shall use Redis for session storage" is a design decision that belongs in an ADR
(see `technical-decision-making`), because it forecloses alternatives without
stating the need it serves. And **compound requirements** — anything containing
"and" that could be half-implemented needs splitting, or you cannot record
partial completion honestly.

### A Real Spec Fragment

Written out in full, because the shape matters as much as the rules.

```
REQ-IMP: Bulk Transaction Import
================================

Context: finance leads reconcile month-end by exporting from their ERP and
comparing against our ledger by hand (see user-needs-discovery findings,
2026-05). Import removes the manual re-keying step.

Actors: user with the "finance" role; the ledger service; the audit log.

FUNCTIONAL

REQ-IMP-001  A user with the "finance" role can upload a UTF-8 CSV of
             transactions for their own organisation.
REQ-IMP-002  Required columns: date (ISO 8601), amount (decimal, 2 dp),
             currency (ISO 4217), description (≤ 500 chars), external_id
             (≤ 64 chars). Column order is not significant; the header row
             is required. Unrecognised columns are ignored and reported.
REQ-IMP-003  Import is atomic per row, not per file: a malformed row is
             rejected individually and valid rows in the same file import.
REQ-IMP-004  Each import produces a record with: id, uploader, filename,
             SHA-256 of content, row counts (total/imported/rejected),
             status (pending|running|complete|partial|failed), start and
             end timestamps.
REQ-IMP-005  Rejected rows are reported with the 1-based source row number
             and a machine-readable reason code.
REQ-IMP-006  A file whose content hash matches a prior import for the same
             organisation within 30 days is rejected as a duplicate.
REQ-IMP-007  Rows whose external_id already exists in the ledger update the
             existing transaction rather than creating a second one.
REQ-IMP-008  Every import writes one immutable audit entry: actor, org,
             filename, content hash, row counts, outcome, timestamp.

NON-FUNCTIONAL

REQ-IMP-100  A 100,000-row file completes within 60 s at p95, measured from
             upload completion to status "complete".
REQ-IMP-101  Up to 200 imports may run concurrently across the platform
             without breaching REQ-IMP-100.
REQ-IMP-102  Uploaded files are encrypted at rest (AES-256) and deleted
             within 24 h of terminal status.
REQ-IMP-103  Zero acknowledged rows lost: any row reported as imported is
             durably committed before the status becomes complete/partial.
REQ-IMP-104  Import endpoints emit a trace span with org id, import id,
             row count, duration, and outcome.

OUT OF SCOPE (v1)

- Excel (.xlsx) upload — CSV only
- Scheduled or recurring imports
- Post-import editing (delete the import and re-upload)
- Multi-currency files; a file must be single-currency (REQ-IMP-002 enforces
  a single value in the currency column)

OPEN QUESTIONS

| # | Question | Owner | Needed by |
|---|---|---|---|
| Q1 | Retention period for rejection reports | @dpo | 2026-08-15 |
| Q2 | Do we surface duplicates by hash across orgs? | @javen | 2026-08-01 |
```

Note what each part buys you. Context stops the requirement being re-litigated
in six months. Out-of-scope stops scope creep and, just as importantly, stops
two teams each assuming the other is doing multi-currency. Open questions with
owners and dates stop an unresolved decision from silently becoming whatever the
first implementer guessed.

### Acceptance Criteria in Given/When/Then

Given establishes state. When is exactly one action. Then asserts observable
outcomes. No UI mechanics, no implementation, no assertions about internals a
user could never see.

```gherkin
Feature: Bulk transaction import
  Covers REQ-IMP-001 .. REQ-IMP-008

Background:
  Given I am authenticated as "ana@acme.test" with the "finance" role
  And my organisation "Acme" has 0 transactions

# REQ-IMP-001, REQ-IMP-004
Scenario: Clean file imports fully
  When I upload "june.csv" with 1,200 valid rows
  Then 1,200 transactions exist for "Acme" within 60 seconds
  And the import record shows status "complete", 1200 imported, 0 rejected
  And the import record stores the SHA-256 of the uploaded content

# REQ-IMP-003, REQ-IMP-005
Scenario: Malformed rows are rejected individually
  When I upload a file of 1,000 rows where rows 5, 90 and 402 have
    a non-numeric amount
  Then 997 transactions exist for "Acme"
  And the import record shows status "partial", 997 imported, 3 rejected
  And the rejection report contains exactly rows 5, 90 and 402
  And each rejection reason code is "AMOUNT_NOT_DECIMAL"
  And no transaction exists with the external_id from rows 5, 90 or 402

# REQ-IMP-007
Scenario: Repeated external_id updates rather than duplicates
  Given a transaction exists with external_id "ERP-88231" and amount 100.00
  When I upload a file whose only row has external_id "ERP-88231"
    and amount 250.00
  Then exactly one transaction exists with external_id "ERP-88231"
  And its amount is 250.00
  And the import record shows 1 imported, 0 rejected
```

Faults to catch in review:

❌ `When I click "Upload" and then click "Confirm"` — two actions and UI
mechanics. A failure will not say which step broke, and the scenario dies the
day the button is renamed.
✅ One action, expressed as intent: `When I upload "june.csv"`.

❌ `Then the import works correctly` — unfalsifiable, so it will pass forever.
✅ Name the observable state: counts, status, records, timings.

❌ `Then a row is inserted into the imports table with status_id = 3` — asserts
implementation, so a schema change breaks a test that describes correct
behaviour.
✅ Assert what an actor can observe: `the import record shows status "complete"`.

❌ `Given the system is set up` — an invisible precondition, so the reader
cannot tell what state the scenario actually depends on.
✅ Spell out only the state the scenario needs, and put shared state in
`Background`.

### Specifying Edge Cases on Purpose

Left unspecified, edge behaviour gets invented by whoever implements it, and
discovered by a customer. Walk a fixed checklist against every input and every
operation.

| Dimension | Ask |
|---|---|
| Empty | Zero rows, empty file, empty string, null, absent field |
| One | Exactly one row — off-by-one and pluralisation |
| Many | Typical volume |
| Boundary | Exactly at the limit, and one over |
| Wrong type | Text in a numeric column, wrong encoding, wrong delimiter |
| Duplicate | Same file twice; same key twice within one file |
| Concurrent | Two imports of the same file at once; import during a read |
| Interrupted | Connection drop, worker crash, deploy mid-run |
| Ordering | Out-of-order rows, out-of-order events |
| Authorisation | Right person wrong org; revoked mid-operation |

Worked examples for this feature:

```gherkin
# Boundary — exactly at, and one over
Scenario Outline: Row-count limit
  When I upload a file with <rows> valid rows
  Then the outcome is <outcome>
  Examples:
    | rows      | outcome                                   |
    | 0         | rejected, 400, reason "FILE_HAS_NO_ROWS"  |
    | 1         | imported, status "complete", 1 imported   |
    | 2000000   | imported, status "complete"               |
    | 2000001   | rejected, 413, message names the 2,000,000 limit |

# Interrupted mid-flight — REQ-IMP-103
Scenario: Worker crashes halfway through
  Given an import of 100,000 rows is running
  And 40,000 rows have been committed
  When the import worker is killed
  Then the import record reaches status "failed" within 5 minutes
  And the 40,000 committed rows remain visible and are not duplicated
  And re-uploading the same file resumes or restarts without creating
    duplicate transactions for the already-committed external_ids

# Concurrency — REQ-IMP-006
Scenario: Same file uploaded twice simultaneously
  When two uploads of an identical file begin within 100 ms of each other
  Then exactly one import proceeds
  And the other is rejected with HTTP 409 naming the winning import id
  And the total transaction count equals the row count of one file

# Authorisation
Scenario: User cannot import into another organisation
  Given I belong only to organisation "Acme"
  When I upload a file targeting organisation "Globex"
  Then the request is rejected with HTTP 403
  And no transactions are created for either organisation
  And an audit entry records the denied attempt
```

The interrupted and concurrent cases are the ones teams skip and production
finds. Specify them before the incident, not in the postmortem.

### Functional vs Non-Functional, Properly Separated

Functional requirements say what the system does; a missing one means a feature
is absent. Non-functional requirements say how well; a missing one means the
feature exists and is unusable, and it is almost always discovered under load,
in an audit, or by a user with a screen reader.

Every non-functional requirement needs four things: a **metric**, a **target**,
a **measurement point**, and a **window/condition**. Drop any of the four and it
becomes arguable.

| Category | Weak | Strong |
|---|---|---|
| Latency | Fast API | p95 < 200 ms, p99 < 500 ms, measured at the gateway excluding client network, over rolling 5 min at ≥ 500 rps |
| Throughput | Handles load | 2,000 writes/s sustained 1 h with error rate < 0.1% |
| Availability | Highly available | 99.9% monthly (≈ 43 min), measured by external synthetic probe every 30 s, excluding announced maintenance |
| Durability | No data loss | Zero acknowledged writes lost; RPO 5 min, RTO 1 h, verified by quarterly restore drill |
| Capacity | Scalable | 50,000 orgs, 10M transactions/org, 200 concurrent imports |
| Security | Secure | TLS 1.2+ only; AES-256 at rest; audit log append-only, retained 7 years |
| Privacy | GDPR compliant | Deletion request purges all PII within 30 days including backups; verifiable by export |
| Accessibility | Accessible | WCAG 2.2 AA; every flow keyboard-operable; verified with NVDA/Firefox and VoiceOver/Safari |
| Observability | Good logs | Every import emits one span with org id, import id, rows, duration, outcome; alert if p95 exceeds REQ-IMP-100 for 15 min |
| Compatibility | Works everywhere | Latest 2 versions of Chrome, Firefox, Safari, Edge; iOS 17+; Android 13+ |

Percentiles, not averages. A mean of 180 ms is consistent with 5% of users
waiting four seconds, and the average is the one number that reliably hides the
experience you actually shipped.

Attach each non-functional target to a monitor at specification time. A target
nobody measures is a target nobody meets — you simply find out later. Where the
target is enforced, say so: a load test in CI, an SLO alert, an axe-core gate.

### Tracing Requirements to Tests

Stable ids plus references in both directions. The ids must never be renumbered;
if a requirement dies, mark it withdrawn and keep the id.

```python
def test_partial_import_rejects_bad_rows(client, org):
    """REQ-IMP-003, REQ-IMP-005: malformed rows rejected individually."""
    result = import_csv(client, rows=make_rows(1000, bad_amount_at=[5, 90, 402]))

    assert result.status == "partial"
    assert result.imported == 997
    assert [r.row for r in result.rejections] == [5, 90, 402]
    assert all(r.code == "AMOUNT_NOT_DECIMAL" for r in result.rejections)
```

A matrix, generated from those docstring references rather than maintained by
hand, closes the loop:

| Req | Tests | Status |
|---|---|---|
| REQ-IMP-003 | `test_partial_import_rejects_bad_rows`, `test_partial_import_keeps_good_rows` | Covered |
| REQ-IMP-006 | `test_duplicate_hash_rejected`, `test_concurrent_duplicate_upload` | Covered |
| REQ-IMP-103 | `test_worker_crash_preserves_committed_rows` | Covered |
| REQ-IMP-101 | — | **Gap** |

Two gaps are worth chasing. A **requirement with no test** is an assumption you
are shipping on. A **test with no requirement** is either dead weight or an
undocumented requirement someone encoded in a hurry — and the second case is
common enough that it is always worth asking rather than deleting.

Coverage here means requirement coverage, which is a different and more useful
question than line coverage. 95% of lines executed says nothing about whether
the duplicate-upload rule was ever exercised.

### Keeping the Spec Alive

Specs rot the moment implementation diverges, and a spec known to be wrong is
worse than none because people still quote it.

- **One source of truth.** The spec lives in one place; slide decks and Slack
  threads link to it and never restate it.
- **Change by amendment.** Editing a requirement in place erases the history of
  why. Mark superseded requirements withdrawn, with a date and a reason, and add
  the replacement with a new id.
- **Behaviour changes touch the spec in the same PR.** If the code and the spec
  disagree, that is a review comment, not a follow-up ticket.
- **Executable where it pays.** Gherkin scenarios wired to real step definitions
  cannot silently drift. For the rest, the traceability matrix is the check.
- **Right-sized.** A two-day change does not need this apparatus; a payments
  integration or anything under audit does. See `feature-planning` for scoping
  and `technical-decision-making` for how much rigour a decision deserves.

## Common Anti-Patterns

❌ **"The system should be fast"** — unfalsifiable, so it is never met and never
violated; every party reads their own number into it.
✅ "p95 < 200 ms at 500 rps, measured server-side over a rolling 5 min window."

❌ **Averages as targets** — a 180 ms mean hides a 4 s tail affecting 5% of users.
✅ Specify p95 and p99, and monitor both.

❌ **Solutions written as requirements** — "shall use Redis" forecloses design
and hides the actual need.
✅ State the need ("sessions survive an app-server restart"); record the choice
in an ADR.

❌ **Compound requirements** — "the system shall validate and import and notify"
cannot be partially completed honestly.
✅ One verifiable behaviour per requirement, each separately testable.

❌ **Given/When/Then with several actions in the When** — a failure cannot be
localised to a step.
✅ Exactly one action per scenario; split the rest.

❌ **Acceptance criteria asserting implementation** — `status_id = 3` breaks on
a schema change that did not break behaviour.
✅ Assert only what an actor can observe.

❌ **Criteria written after the code** — they describe what was built, so they
can never fail and never catch a regression in intent.
✅ Write and review criteria before implementation begins.

❌ **No edge cases** — empty, boundary, duplicate, concurrent, and interrupted
paths get invented silently during implementation.
✅ Walk the edge-case checklist for every input and operation.

❌ **Non-functional requirements with no monitor** — a target nobody measures is
discovered unmet in an incident.
✅ Bind each target to an alert, an SLO, or a CI gate at spec time.

❌ **Renumbered or in-place-edited requirements** — history and traceability both
vanish.
✅ Immutable ids; withdraw and supersede rather than overwrite.

❌ **Open questions with no owner** — the unresolved decision defaults to the
first implementer's guess, discovered in QA.
✅ Every open question has a named owner and a date it is needed by.

❌ **No out-of-scope section** — the most expensive rework is work nobody asked
for, or work each team assumed the other was doing.
✅ State exclusions explicitly, including the tempting adjacent ones.

❌ **A spec only its author can interpret** — the real test is whether someone
who was not in the room can implement it.
✅ Hand it to an uninvolved engineer and collect their questions; each question
is a defect in the spec.

## Requirements Specification Checklist

- [ ] Every requirement is falsifiable — a failing check could be written
- [ ] No instance of fast, scalable, intuitive, robust, seamless, or "handle"
- [ ] Each requirement states one behaviour, not several joined by "and"
- [ ] Requirements state needs, not chosen technologies
- [ ] Every requirement has a stable, never-reused id
- [ ] Context recorded: what problem this solves and for whom
- [ ] Actors and their permissions named explicitly
- [ ] Acceptance criteria written before implementation
- [ ] Each scenario has exactly one action in its When step
- [ ] Assertions describe observable outcomes, not internal state
- [ ] Preconditions explicit; no "the system is set up"
- [ ] Edge-case checklist walked: empty, one, boundary, over-boundary, wrong
      type, duplicate, concurrent, interrupted, ordering, authorisation
- [ ] Failure behaviour specified, including partial failure and rollback
- [ ] Functional and non-functional requirements separated
- [ ] Every non-functional requirement has metric, target, measurement point,
      and window
- [ ] Percentiles used rather than averages
- [ ] Each non-functional target bound to a monitor, SLO, or CI gate
- [ ] Security, privacy, accessibility, and observability each addressed
- [ ] Out-of-scope items listed explicitly
- [ ] Open questions carry a named owner and a due date
- [ ] Every requirement traced to at least one test id
- [ ] Every test traced back to a requirement, or explicitly justified
- [ ] Traceability gaps reviewed before sign-off
- [ ] Reviewed by someone who was not in the room when it was written
