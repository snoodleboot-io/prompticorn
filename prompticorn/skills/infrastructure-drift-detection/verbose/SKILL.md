# Infrastructure Drift Detection (Verbose)

## Core Patterns

### Where Drift Actually Comes From

Drift is the divergence between declared infrastructure and live infrastructure.
Naming its sources matters because they call for different remedies.

| Source | Example | Remedy |
|---|---|---|
| Emergency console change | Security group widened during an incident | Remove standing write access; codify after |
| Convenience console change | "Just bumping the instance size" | Same — plus a faster pipeline |
| Provider defaults | Tags, ARNs, or KMS keys injected at create | Codify the default, or ignore narrowly |
| Controllers and autoscalers | `desired_count`, node group size | Narrow `ignore_changes` |
| Out-of-band automation | A Lambda that rotates a rule | Bring it into code or exclude explicitly |
| Manual state surgery | `state rm` after a botched apply | Review process; import rather than remove |

The dominant source, by a wide margin, is the first two. Someone with production
console access fixes a real problem in ninety seconds and does not come back to
write it down — because the incident is over and the fix is working.

What makes this expensive is the delay. The infrastructure is now correct and the
code is now wrong, and nothing reports the discrepancy. Weeks later an unrelated
pull request adds a tag; the plan includes a quiet `~` line narrowing that security
group back to its declared value; the apply reproduces the original outage with no
apparent cause. The eventual timeline reconstruction (see
`incident-timeline-creation`) will show a deploy that "changed nothing relevant".

### The Detection Mechanism

`terraform plan` refreshes state against the provider APIs and diffs. The flag that
makes it automatable is `-detailed-exitcode`:

```bash
terraform init -input=false
terraform plan -detailed-exitcode -lock-timeout=5m -out=drift.tfplan
```

| Exit code | Meaning | Job behaviour |
|---|---|---|
| 0 | No changes | Success, no notification |
| 1 | Error — credentials, lock contention, API failure | Page the platform team |
| 2 | Changes present | Drift finding: report and route |

Collapsing 1 and 2 into "non-zero means drift" is the most common implementation
bug: an expired credential then looks identical to a clean run of findings, and a
persistently broken job reads as persistent drift until someone stops looking.

One important caveat: a scheduled plan against `main` reports both true drift *and*
merged-but-unapplied code. Run the check against the ref that is actually deployed
— tag it on apply and check out that tag — or you will spend your first month
triaging your own backlog.

For a read-only check without producing a plan artifact, newer Terraform supports
`terraform plan -refresh-only -detailed-exitcode`, which reports only changes the
provider made outside Terraform and excludes changes originating in your code.
That is usually the more precise drift signal.

### Scheduling

Drift detection belongs on a timer, not in the deploy pipeline. Checking at deploy
time is checking at the moment it is most expensive to act: the finding lands in
front of an engineer who is trying to ship something unrelated, mixed into a plan
they are about to approve.

```yaml
name: drift-detection
on:
  schedule:
    - cron: "0 */6 * * *"
  workflow_dispatch: {}

permissions:
  id-token: write
  contents: read

jobs:
  detect:
    strategy:
      fail-fast: false
      matrix:
        stack: [network, data, platform, apps]
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ env.DEPLOYED_REF }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/tf-drift-readonly
          aws-region: us-east-1
      - run: terraform -chdir=infra/${{ matrix.stack }}/prod init -input=false
      - id: plan
        continue-on-error: true
        run: |
          terraform -chdir=infra/${{ matrix.stack }}/prod \
            plan -refresh-only -detailed-exitcode -lock-timeout=5m -out=drift.tfplan
      - if: steps.plan.outcome == 'failure' && steps.plan.conclusion != 'success'
        run: ./scripts/report-drift.sh infra/${{ matrix.stack }}/prod/drift.tfplan
```

Cadence guidance:

| Environment | Interval | Rationale |
|---|---|---|
| Regulated / PCI / HIPAA | Hourly | Evidence requirement; short unauthorized-change window |
| Production | 4–6 hours | Catches same-day drift while the context is fresh |
| Staging | Daily | Lower stakes, still worth trending |
| Ephemeral | Never | Rebuilt from code anyway |

Two hard rules for the scheduled job:

**Read-only credentials.** The role should hold `Describe*`/`Get*`/`List*` and
nothing else. This is not merely defence in depth — it makes the next rule
structurally impossible to violate.

**Never auto-apply.** An auto-remediating drift job reverts the mitigation an
on-call engineer put in place, unattended, in the middle of the night, with no
human in the loop. The correct output of a drift job is a notification.

### Reporting

Raw plan output is unreadable at 200 lines. Parse the JSON:

```bash
terraform show -json drift.tfplan | jq -r '
  .resource_changes[]
  | select(.change.actions | inside(["no-op"]) | not)
  | "\(.change.actions | join(",")) \(.address)"
'
```

For attribute-level detail:

```bash
terraform show -json drift.tfplan | jq -r '
  .resource_changes[]
  | select(.change.actions[0] == "update")
  | .address as $a
  | .change.before as $b
  | .change.after  as $x
  | ($b | keys[]) as $k
  | select($b[$k] != $x[$k])
  | "\($a).\($k): \($b[$k]) -> \($x[$k])"
'
```

A good report answers three questions: which resource, which attribute, and who
changed it. The third comes from the audit log, not from Terraform:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-0abc123 \
  --start-time "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --query 'Events[].[EventTime,Username,EventName]' --output table
```

Route by owning team using resource tags. A shared `#infra-alerts` channel that
receives every finding for every stack is a channel people mute within a fortnight.

### Triage: Codify, Revert, or Ignore

Every finding resolves to exactly one of three outcomes, and leaving it unresolved
is what makes drift chronic.

**Codify** when the manual change was correct. Write it into the module, open a
PR, let the plan confirm it produces no diff, apply. This is the common case for
incident mitigations, and it is the step teams skip.

**Revert** when the change was unauthorized or accidental. Apply the declared
configuration — after confirming with the owning team that nothing depends on the
live value. Then ask how the write happened; an unexplained production change is a
security finding, not just a hygiene one.

**Ignore** when the attribute is legitimately owned by something else:

```hcl
resource "aws_ecs_service" "api" {
  # ...
  lifecycle {
    ignore_changes = [
      desired_count,                 # managed by application autoscaling
      task_definition,               # managed by the deploy pipeline
    ]
  }
}
```

Name the attributes. `ignore_changes = all` converts the resource into a permanent
blind spot — it will never report drift again, including a security group opened to
the internet.

### Complementary Controls

Terraform plan sees only what Terraform manages. Two gaps need separate coverage:

**Unmanaged resources.** Anything created outside code is invisible to plan
entirely. Cloud-native config tooling — AWS Config rules, Azure Policy, GCP
Organization Policy — evaluates every resource regardless of provenance, and is the
right place for absolute rules like "no security group allows 0.0.0.0/0 on 22".

**Preventive guardrails.** Service control policies and IAM boundaries that deny
the mutating action outright beat detecting it afterwards. Drift detection is a
backstop for what the guardrails allow through.

Track findings over time. A resource that drifts on the same attribute every week
is telling you the code is wrong, or the team's real workflow does not route
through the pipeline. That is a process defect — feed it into the improvement loop
(see `continuous-improvement`), because remediating it individually forever is not
a solution.

## Common Anti-Patterns

❌ **Detecting drift only during a deploy** — the finding arrives when it is most
disruptive and least likely to be triaged properly.
✅ Scheduled detection every few hours, decoupled from releases.

❌ **Treating exit codes 1 and 2 as the same** — an expired credential is
indistinguishable from clean findings, and a broken job looks like a busy one.
✅ Branch on the exit code: 1 pages, 2 reports.

❌ **Auto-applying to "self-heal"** — unattended reversion of an on-call
engineer's mitigation, usually reproducing the original incident.
✅ Report only; humans decide codify, revert, or ignore. Read-only credentials
make this enforceable.

❌ **`ignore_changes = all`** — silences the alarm rather than fixing the noise,
including for changes that matter.
✅ Ignore specific attributes, with a comment naming what owns them.

❌ **Planning against `main` and calling unapplied code "drift"** — floods the
report with your own pending changes.
✅ Check against the deployed ref, or use `-refresh-only` to isolate external
changes.

❌ **Standing production console write access for the whole team** — this is the
drift source; detection alone cannot outrun it.
✅ Read-only by default, time-boxed break-glass that alerts on assumption.

❌ **Findings that are noted and forgotten** — the same drift reappears every
scheduled run and everyone learns to ignore the report.
✅ Every finding gets an owner and a resolution: codified, reverted, or ignored
with justification.

❌ **Assuming plan covers everything** — resources created outside Terraform never
appear in a plan at all.
✅ Pair with AWS Config / Azure Policy / GCP Org Policy for provenance-independent
evaluation.

## Drift Detection Checklist

- [ ] Scheduled drift job on production, every 4–6 hours or better
- [ ] Job runs against the deployed ref, not the tip of `main`
- [ ] `-detailed-exitcode` used, with 1 and 2 handled differently
- [ ] `-refresh-only` used where the goal is external-change detection
- [ ] Detection role is strictly read-only
- [ ] Job never applies
- [ ] Findings parsed to resource and attribute level, not raw plan text
- [ ] Reports routed to owning teams by tag
- [ ] Audit log correlation identifies who made each change
- [ ] Every finding closed as codify / revert / ignore-with-reason
- [ ] `ignore_changes` scoped to named attributes; no `all`
- [ ] Humans have no standing production write access
- [ ] Cloud-native policy evaluation covers unmanaged resources
- [ ] Recurring drift on the same resource escalated as a process defect
