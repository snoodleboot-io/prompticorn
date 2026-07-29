# Workflow Security In Workflows Workflow

Securing the orchestration layer itself: what a run is allowed to do, what it
carries, and what it leaves behind.

Workflows are a distinctive target. They hold broad, long-lived credentials, run
unattended with no human to notice anomalies, and touch many systems in one pass —
so a single compromised step often reaches further than a compromised service would.

---

## 1. Identity per step, not per workflow

The default failure is one service account with the union of every permission any
step ever needed. Compromise anywhere yields all of it.

### Characteristics:
- Each step assumes its **own** short-lived identity
- Permissions are scoped to that step's actual resources
- Credentials are issued at step start and expire before the run ends

### Implementation:
```yaml
steps:
  - id: read_orders
    identity: role/workflow-orders-reader
    permissions: [s3:GetObject on bucket/orders/*]
    credential_ttl: 15m

  - id: write_report
    identity: role/workflow-report-writer
    permissions: [s3:PutObject on bucket/reports/*]
    credential_ttl: 15m
```

The reader cannot write; the writer cannot read source data. Neither can touch
anything else.

### Advantages & Disadvantages:
- **Advantage:** Blast radius collapses to one step's scope
- **Advantage:** Permissions become documentation of what a step actually does
- **Disadvantage:** More roles to manage — generate them from the definition rather
  than hand-maintaining them

---

## 2. Secrets: reference, never embed

### Implementation:
```yaml
env:
  DB_PASSWORD: {secret_ref: vault://db/prod#password}   # resolved at step start
  API_KEY:     {secret_ref: vault://api/key, ttl: 1h}
```

Rules that matter:
- **Never in the definition.** Workflow definitions are versioned, diffed, and
  widely readable — a secret committed there is a secret disclosed.
- **Never in parameters.** Run parameters are logged, displayed in UIs, and stored
  in run history.
- **Resolve at execution, in memory,** and never write the resolved value to disk
  or to the run record.
- **Prefer short-lived dynamic credentials** over static secrets. A leaked 15-minute
  credential is a much smaller event.

---

## 3. Redact at the boundary

A workflow that handles sensitive data leaks it through logs, error messages, run
records, and metrics far more often than through its actual output.

### Implementation Strategy:
```yaml
redaction:
  fields: [password, token, ssn, card_number, email]
  apply_to: [logs, run_records, error_messages, traces, metrics_labels]
  strategy: hash_with_salt      # keeps records correlatable without exposing values
on_unknown_field: redact        # deny-list by default
```

Two rules do most of the work:
- **Redact in error paths too.** Exception messages that echo the failing payload
  are the most common leak — the happy path is usually clean and the error path is not.
- **Never put user data in metric labels.** It becomes high-cardinality *and*
  permanently retained in a system with weaker access controls than your database.

---

## 4. Validate inputs — a trigger is an entry point

A workflow triggered by an external event, a file landing, or an API call has an
attacker-controlled input, and steps frequently interpolate it into shell commands,
SQL, or file paths.

```yaml
trigger:
  source: s3://uploads/
  validate:
    filename: "^[a-zA-Z0-9_-]+\\.csv$"    # allow-list, not deny-list
    max_size: 100MB
    content_type: text/csv
  quarantine_on_reject: true
```

- **Allow-list the shape** of every externally-supplied parameter
- **Never interpolate parameters into a shell command.** Pass them as arguments
- **Treat path parameters as hostile** — `../` traversal via a workflow parameter
  is a recurring finding
- Bound the size; an unbounded input is a denial-of-service against the whole
  worker pool

---

## 5. Approval gates for privileged actions

Some steps should not run unattended.

```yaml
- id: delete_production_data
  requires_approval:
    approvers: group/data-owners
    min_approvals: 2
    expires_in: 4h
    approval_is_binding_to: {run_id, inputs_digest}
```

Bind the approval to the **exact run and its inputs**. An approval that can be
reused for a later run with different inputs is a confused-deputy problem, and it
is the usual way approval gates are implemented wrong.

Separation of duties: whoever authored or deployed the change should not be the
sole approver of its privileged execution.

---

## 6. Audit trail

An audit log that cannot answer "who caused this, with what input, under whose
authority" is decoration.

```yaml
audit:
  record: [run_id, workflow_version, trigger_source, triggering_principal,
           inputs_digest, per_step_identity, approvals, outputs_digest]
  immutable: true
  retention: 400d           # exceed the longest applicable audit period
  tamper_evident: append_only_with_chaining
```

Log the **principal that triggered the run**, not just "scheduler". A manual run
attributed to the service account is an untraceable action.

---

## Supply chain

The definition and its steps are code, and they run with production credentials.

- Pin step images and dependencies by **digest**, not by mutable tag
- Require review on definition changes as strictly as on application code — a
  one-line edit to a definition can exfiltrate a database
- Scan step images for known vulnerabilities on a schedule, not only at build
- Restrict who can register or modify a workflow, and audit those changes separately

---

## Best Practices

1. **A distinct, least-privilege identity per step,** with short-lived credentials.
2. **Secrets by reference only** — never in definitions, parameters, or run records.
3. **Redact on error paths,** not just the happy path.
4. **Never put user data in metric labels.**
5. **Allow-list external inputs;** treat every trigger as an entry point.
6. **Bind approvals to the run id and inputs digest.**
7. **Record the triggering principal** in an immutable, append-only audit trail.
8. **Pin step images by digest** and review definition changes like production code.

---

## Common Pitfalls

- **One service account for the whole workflow.** Any step's compromise yields everything.
- **Secrets passed as run parameters.** They land in logs, UIs, and run history.
- **Redaction only on the success path.** The exception message carries the payload.
- **User identifiers as metric labels.** Permanent retention in a weakly-controlled store.
- **Shell interpolation of parameters.** Command injection via a trigger.
- **Reusable approvals.** Approved once, replayed against different inputs.
- **Mutable image tags.** The reviewed step is not the step that ran.
- **Audit logs without the triggering principal.** No accountability.

---

## Related Patterns

- `workflow-compliance-patterns` — turning these controls into evidence
- `workflow-monitoring` — detecting anomalous runs and privilege use
- `secret-management` — issuing and rotating the credentials referenced here
- `security-hardening-checklist` — the broader system-level controls