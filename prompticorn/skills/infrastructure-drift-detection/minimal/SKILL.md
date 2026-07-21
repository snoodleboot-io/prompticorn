# Infrastructure Drift Detection (Minimal)

## Purpose
Find the gap between what your code says the infrastructure is and what it actually is — on a schedule, before an unrelated deploy discovers it for you.

## Core Techniques

### 1. Know Where Drift Comes From
Almost all of it is manual console and CLI changes made under pressure: someone widens a security group at 2am, bumps an RDS instance class, or edits an autoscaling minimum to stop a page. The fix works, the incident ends, and nobody writes it back into code. Other sources: cloud provider defaults injected on create, resources mutated by controllers or autoscalers, and out-of-band automation with its own credentials.

The dangerous property is latency. Drift is silent until the next apply, which quietly reverts the 2am fix — often reproducing the original outage, now with no obvious cause.

### 2. Use `-detailed-exitcode` as the Signal
```bash
terraform plan -detailed-exitcode -lock-timeout=5m -out=drift.tfplan
```
| Exit code | Meaning |
|---|---|
| 0 | No changes — infrastructure matches code |
| 1 | Error (auth, lock, network) |
| 2 | Changes present — drift or unmerged code |

That is a machine-readable boolean you can alert on. Treat 1 and 2 differently: an error is an operations problem, a 2 is a drift finding.

### 3. Run It On a Schedule, Not On Deploy
Drift checks at deploy time tell you too late — the change is already queued behind a plan someone is about to approve. Run every 4-6 hours (hourly for regulated or high-churn accounts) against a clean checkout of the deployed ref.
```yaml
on:
  schedule:
    - cron: "0 */6 * * *"
```
Use a read-only role and never auto-apply the result. A scheduled job that fixes drift by applying is a scheduled job that reverts emergency mitigations at 3am.

### 4. Report What Actually Changed
```bash
terraform show -json drift.tfplan \
  | jq -r '.resource_changes[]
      | select(.change.actions[0] != "no-op")
      | "\(.change.actions[0]) \(.address)"'
```
Route findings to the owning team, not a shared firehose. Include the resource address, the changed attributes, and — where the provider supports it — the CloudTrail/Activity Log entry naming who made the change.

### 5. Decide Per Finding: Codify, Revert, or Ignore
| Finding | Action |
|---|---|
| Someone fixed something real by hand | Codify it — write it back into the module, then apply |
| Unauthorized or accidental change | Revert via apply, and review the access that allowed it |
| Provider-managed attribute that always differs | `ignore_changes`, narrowly |

```hcl
lifecycle {
  ignore_changes = [ desired_count ]   # owned by the autoscaler, not by us
}
```
Scope `ignore_changes` to named attributes. `ignore_changes = all` turns the resource into an unmonitored blind spot.

### 6. Reduce the Supply
Detection is the backstop; removing write access is the fix. Humans read-only in production, break-glass roles that are time-boxed and alert on assumption, and a fast enough pipeline that the console is never the quicker option.

## Warning Signs

- Drift only discovered during an unrelated deploy
- No scheduled plan job — checks run only when someone remembers
- Scheduled job auto-applies, silently reverting live mitigations
- Engineers hold standing write access to the production console
- `ignore_changes = all` on resources, hiding real changes
- Drift reports go to a channel nobody owns
- Findings recorded but never codified, so the same drift reappears every week
- `terraform plan` exit code discarded because the job uses plain `plan`
