# Compliance Automation (Minimal)

## Purpose
Make controls prove themselves continuously — checked by code, evidenced by machines — instead of reconstructing a year of assurance in the four weeks before an audit.

## Core Techniques

### 1. Continuously Monitor Controls Instead of Testing Them Annually
An annual test tells you a control worked on one day. Period-based audits ask whether it worked throughout, so run the test on the control's natural cadence — continuously for configuration, daily for access, per-change for the pipeline — and store each result as a dated record.

```
Control  : Production data stores are encrypted at rest
Check    : query every storage resource in the production accounts, assert encryption enabled
Cadence  : every 30 minutes, plus on every infrastructure change
Result   : timestamped pass/fail per resource, retained 18 months
Failure  : ticket to the owning team; blocks release if the resource is new
```

The by-product is the evidence. A year of dated check results is stronger than any screenshot, and it costs nothing extra at audit time.

### 2. Collect Evidence as Code
Write evidence collectors the same way you write tests: versioned, reviewed, scheduled, and idempotent. Each collector names the control it serves, pulls from an authoritative system API, and writes an immutable, timestamped artifact with its own provenance.

```
collectors/
  access_review.py      -> IdP roles + HR status, per quarter
  encryption_state.py   -> storage/database encryption flags, per 30 min
  change_records.py     -> merged PRs with approvals and CI results, daily
  backup_restore.py     -> restore test outcome and duration, monthly
  vuln_posture.py       -> scan findings with age against SLA, daily
```

Record where each artifact came from and when. Evidence whose provenance cannot be explained is evidence an auditor will discount.

### 3. Express Policy as Code
A policy in a document is an intention; a policy in the pipeline is a control. Encode the rule once and enforce it at the gate.

```rego
package compliance.storage

# Deny any object store that is public or unencrypted.
deny contains msg if {
    bucket := input.resource.aws_s3_bucket[name]
    bucket.acl == "public-read"
    msg := sprintf("bucket %v is publicly readable", [name])
}

deny contains msg if {
    bucket := input.resource.aws_s3_bucket[name]
    not bucket.server_side_encryption_configuration
    msg := sprintf("bucket %v has no encryption configured", [name])
}
```

The same rules can run in three places: pre-merge against the plan, at admission time in the cluster, and continuously against deployed state. Cloud Custodian covers the last of these with declarative policies that filter resources and take actions — tag, notify, or remediate — on a schedule.

### 4. Detect Drift on Controls, Not Just Infrastructure
Resources are changed outside the pipeline, and a control that was in place in January may not be in June. Compare the declared state against reality on a schedule and alert on the difference. Treat every drift event as a finding with a cause: a broken pipeline, a missing guardrail, or a legitimate emergency change that never made it back into code.

### 5. Automate Access Reviews
Manual quarterly reviews are the control that most often exists on paper only. Generate the review: join the identity provider's grants with the HR system's employment status and the ticket that authorised each grant, then push each reviewer only their own list with a deadline. Record reviewer, date, decision, and the revocation that followed — the revocation is the part auditors check.

Deprovisioning should not wait for the review at all. Drive it from the HR system on the day someone leaves or changes role.

### 6. Protect Audit-Log Integrity
Logs are only evidence if they cannot be quietly edited. Ship them off the originating host promptly, write to append-only or write-once storage, deny delete permissions to everyone including administrators and the shipping identity, retain for the required period, and monitor for gaps and for changes to the logging configuration itself. A log pipeline that can be disabled without an alert is not an audit trail.

### 7. Track Coverage, Not Just Passes
Report which controls are automatically checked and which are still manual. The dangerous state is a dashboard showing 100% pass across the third of controls that happen to be automated, while the rest go unexamined.

## Warning Signs

- Screenshots in a shared folder as the primary evidence store
- Evidence collected only in the weeks before fieldwork
- Policies written in documents but not enforced at any gate
- Checks that run in CI only, so post-deploy drift is invisible
- Access reviews signed off with no record of resulting revocations
- Audit logs deletable by the same administrators they are meant to observe
- A green compliance dashboard that omits the unautomated controls
- Automated findings raised with no owner, ageing indefinitely
