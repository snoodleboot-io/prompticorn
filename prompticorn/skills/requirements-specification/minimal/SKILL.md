# Requirements Specification (Minimal)

## Purpose
Write requirements a stranger could implement and a tester could falsify, so
"done" is a fact rather than an argument in review.

## Core Techniques

### 1. Every Requirement Must Be Falsifiable
The test: could someone write a check that fails? If not, it is a wish.

| ❌ Not a requirement | ✅ Requirement |
|---|---|
| The system should be fast | Search returns p95 < 200 ms at 500 req/s sustained, measured server-side at the API boundary |
| The UI should be intuitive | A first-time user completes account creation in under 90 s with no help, in 8 of 10 moderated sessions |
| Handle large files | Accepts CSV uploads to 500 MB / 2M rows; rejects larger with HTTP 413 and a message naming the limit |
| Should be secure | All endpoints require a valid bearer token; tokens expire in 15 min; failed auth returns 401 with no detail |
| Support many users | 10,000 concurrent sessions with error rate < 0.1% and p99 < 800 ms |
| Errors should be handled gracefully | On upstream timeout (>3 s), return 503 with Retry-After: 30 and preserve the user's draft |

Vague words that signal an unwritten requirement: fast, scalable, intuitive,
robust, seamless, user-friendly, appropriate, as needed, etc., and any use of
"handle". Each hides a number nobody has agreed.

### 2. Write Acceptance Criteria in Given/When/Then
One scenario per behaviour. Given is state before, When is exactly one action,
Then is an observable result — no UI steps, no implementation.

```gherkin
Feature: Bulk transaction import

Scenario: Valid file imports successfully
  Given I am authenticated as a user with the "finance" role
  And my organisation has 0 imported transactions
  When I upload "transactions-2026-06.csv" containing 1,200 valid rows
  Then all 1,200 transactions appear in the ledger within 30 seconds
  And the import record shows status "complete" with 1200 imported, 0 rejected
  And an audit entry records my user id, the filename, and the row count

Scenario: File with some invalid rows imports the remainder
  Given I am authenticated as a user with the "finance" role
  When I upload a file of 1,000 rows where rows 5, 90, and 402 have a
    malformed amount
  Then 997 transactions are imported
  And the import record shows status "partial" with 3 rejected
  And a rejection report lists each row number with the reason
    "amount is not a valid decimal"
  And no partially-written transaction exists for rows 5, 90, or 402
```

The give-away for a bad scenario is "And" in the When step — two actions means
two scenarios, and the failure will not tell you which action broke.

### 3. Specify Edge Cases Deliberately, Not by Accident
For every input, walk a fixed list: empty, one, many, maximum, over maximum,
wrong type, wrong encoding, duplicate, concurrent, and interrupted mid-flight.

```gherkin
Scenario: Duplicate import is rejected, not silently re-run
  Given I successfully imported "june.csv" 10 minutes ago
  When I upload a file with an identical SHA-256 content hash
  Then the request is rejected with HTTP 409
  And the response names the prior import id and its timestamp
  And no new transactions are created

Scenario: Connection drops mid-upload
  Given I am uploading a 400 MB file
  When the connection drops after 60% of bytes are transferred
  Then no transactions from that file appear in the ledger
  And the partial upload is deleted within 1 hour
  And re-uploading the same file succeeds
```

Empty and boundary cases are where production breaks, and they are what
implementers silently invent an answer for when the spec is quiet.

### 4. Separate Functional From Non-Functional
Functional says what the system does; non-functional says how well, and it is
where "should be fast" goes to die.

| Category | Bad | Good |
|---|---|---|
| Performance | Fast import | 1M rows ingested in < 5 min; API p95 < 200 ms at 500 rps |
| Availability | Highly available | 99.9% monthly (≈43 min downtime), excluding announced windows |
| Capacity | Scales well | 50k orgs, 10M rows/org, 200 concurrent imports |
| Durability | Don't lose data | Zero acknowledged writes lost; RPO 5 min, RTO 1 hour |
| Security | Secure | TLS 1.2+; data encrypted at rest with AES-256; audit log immutable 7 years |
| Accessibility | Accessible | WCAG 2.2 AA; full keyboard operation; verified with NVDA and VoiceOver |
| Observability | Good logging | Every import emits a span with org id, row count, duration, outcome |

Each needs a number, a measurement point, and a measurement window. "p95 < 200
ms" without "measured server-side, excluding client network, over a rolling 5
min window at 500 rps" is still arguable.

### 5. Trace Every Requirement to a Test
Give each requirement a stable id and reference it from the test that proves it.

```
REQ-IMP-004  Rows with a malformed amount are rejected individually;
             valid rows in the same file still import.
             -> tests/integration/test_import.py::test_partial_import_rejects_bad_rows
             -> tests/integration/test_import.py::test_partial_import_keeps_good_rows
```

Two questions the trace answers instantly: is every requirement tested, and does
every test exist for a reason? A requirement with no test is an assumption. A
test with no requirement is either dead weight or an undocumented requirement —
and it is worth finding out which.

### 6. State What Is Out of Scope
An explicit exclusion list prevents the most expensive kind of rework: work
nobody asked for, and work everybody assumed someone else had specified.

```
Out of scope for v1:
  - Excel (.xlsx) uploads — CSV only
  - Scheduled or recurring imports
  - Editing transactions after import (delete and re-import instead)
  - Multi-currency conversion; files must be single-currency
Deferred decisions:
  - Retention of rejection reports (owner: @dpo, needed by 2026-08-15)
```

## Warning Signs

- Requirements containing fast, scalable, intuitive, robust, or "handle"
- Acceptance criteria written after implementation, describing what was built
- Given/When/Then with multiple actions in the When step
- Non-functional requirements with no number, no measurement point, no window
- No empty, boundary, duplicate, or concurrent cases anywhere in the spec
- Requirements that name a database table or class instead of a behaviour
- No requirement ids, so no way to check coverage
- Nothing marked out of scope
- Open questions with no owner and no due date
- A spec only the author can interpret without a conversation
