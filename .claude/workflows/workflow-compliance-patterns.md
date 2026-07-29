# Workflow Compliance Patterns Workflow

Making a workflow produce the evidence a regulation requires, as a by-product of
running — rather than reconstructing it during an audit.

`workflow-security-in-workflows` establishes the controls. This workflow is about
*proving* they operated: continuously, with retained evidence, over the whole audit
period.

---

## 1. Evidence is a run output, not an audit-time artifact

The annual scramble exists because controls are tested once, by hand, months after
the fact. A control that emits evidence on every run is tested continuously and
costs nothing at audit time.

### Characteristics:
- Every control has a machine-checkable assertion
- The assertion runs during the workflow, not in a quarterly review
- Its result is retained for the full audit period

### Implementation:
```yaml
controls:
  - id: AC-3-least-privilege
    assert: every_step_has_scoped_identity
    evidence: [step, identity, permissions, credential_ttl]
  - id: AU-2-audit-events
    assert: run_record_complete
    evidence: [run_id, principal, inputs_digest, approvals]
  - id: SC-28-encryption-at-rest
    assert: all_outputs_written_encrypted
    evidence: [target, kms_key_id]
evidence_store:
  immutable: true
  retention: 7y            # the longest applicable period, not the shortest
```

### Advantages & Disadvantages:
- **Advantage:** Audit becomes a query, not a project
- **Advantage:** A control that stops working is detected in days, not at year end
- **Disadvantage:** Retention costs are real — set them from the regulation, not by habit

---

## 2. Data classification drives every other requirement

Nothing downstream can be decided until you know what the workflow handles. The
same pipeline moving public catalogue data and cardholder data has entirely
different obligations.

| Class | Typical constraints |
|-------|---------------------|
| Public | None beyond integrity |
| Internal | Access control, audit |
| PII / personal data | Residency, minimization, subject rights, retention limits |
| Cardholder / health | Encryption, segmentation, strict retention, tighter access |

```yaml
data_classification:
  inputs:  {orders: pii, catalogue: public}
  outputs: {report: internal}
  propagation: highest_wins    # a join of PII and public produces PII
```

**Classification propagates through joins.** Deriving a "clean" dataset from
personal data does not declassify it unless the derivation is genuinely
irreversible — and aggregation usually is not.

---

## 3. Residency and transfer

Where data is processed is a hard constraint, not a preference.

```yaml
residency:
  allowed_regions: [eu-west-1, eu-central-1]
  enforce: reject_run          # fail closed if a step would execute elsewhere
  transfer_mechanism: scc      # required if any step leaves the region
```

Fail the run rather than proceeding. A workflow that silently fails over to another
region has created a reportable transfer, and the failover is exactly when nobody
is watching.

Check the whole path: a step in-region calling an out-of-region API is still a transfer.

---

## 4. Retention and deletion as scheduled work

Retention obligations are two-sided: keep for at least X, and delete after Y. Most
implementations do the first and skip the second.

### Implementation Strategy:
```yaml
retention:
  audit_records:  {min: 7y}
  raw_pii:        {max: 90d,  action: delete}
  derived_reports:{max: 2y,   action: anonymize}
deletion_job:
  schedule: daily
  scope_includes: [backups, caches, search_indices, DLQ, logs]
  verify: assert_absent_after
  evidence: deletion_certificate
```

The **scope is where this goes wrong**. Deleting from the primary store while the
record persists in a backup, a search index, a cache, or a dead-letter queue does
not satisfy a deletion obligation. Enumerate every copy the workflow creates.

---

## 5. Subject rights requests

Under GDPR-style regimes, access and erasure requests are workflows with legal
deadlines, and they must reach the same copies the deletion job does.

```yaml
subject_request:
  types: [access, erasure, rectification, portability]
  sla: 30d
  locate_by: subject_id_index    # you must be able to find every copy
  output_format: intelligible    # decrypted and human-readable, not a raw dump
  evidence: [request_id, located_records, action_taken, completed_at]
```

Two recurring failures: exports that return encrypted or internally-encoded values
(not "intelligible form"), and an erasure that misses derived datasets built from
the subject's data.

---

## 6. Change control

Auditors ask who approved the change and how it was verified.

```yaml
change_control:
  require: [peer_review, linked_ticket, test_evidence, approver != author]
  record: [version, diff, approver, deployed_at, rollback_plan]
```

Separation of duties is checkable: assert `approver != author` in CI rather than
asserting it in a policy document nobody executes.

---

## Best Practices

1. **Emit evidence on every run;** never reconstruct it at audit time.
2. **Classify inputs and outputs explicitly,** and propagate on joins.
3. **Fail closed on residency** rather than failing over out of region.
4. **Enumerate every copy** — backups, caches, indices, DLQ, logs — for deletion.
5. **Implement the delete side of retention,** not only the keep side.
6. **Return subject data in intelligible form,** decrypted and readable.
7. **Assert separation of duties in CI** (`approver != author`).
8. **Set retention from the longest applicable obligation.**

---

## Common Pitfalls

- **Evidence gathered at audit time.** Expensive, and it proves nothing about the
  intervening months.
- **Deleting only from the primary store.** Backups and search indices still hold it.
- **Retaining forever "to be safe."** Over-retention is itself a violation under
  data-protection regimes.
- **Treating aggregates as anonymous.** Most aggregation is reversible enough to
  re-identify.
- **Silent cross-region failover.** Creates an unreported transfer, unobserved.
- **Encrypted subject-access exports.** Fails the intelligible-form requirement.
- **Separation of duties as policy text only.** Unenforced, so it drifts immediately.

---

## Related Patterns

- `workflow-security-in-workflows` — the controls this workflow evidences
- `workflow-monitoring` — detecting a control that has stopped operating
- `compliance-audit` — the audit process these outputs feed
- `workflow-versioning-management` — retaining the definition each record was produced under