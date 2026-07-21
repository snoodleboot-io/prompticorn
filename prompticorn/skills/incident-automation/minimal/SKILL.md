# Incident Automation (Minimal)

## Purpose
Automate the mechanical parts of incident response — routing, setup, remediation, record-keeping — so responders spend their attention on diagnosis rather than logistics.

## Core Techniques

### 1. Turn Runbooks into Executable Steps
A prose runbook rots because nothing fails when it is wrong. Move each step into a script that a responder invokes and that reports what it did.

```bash
# runbooks/db-connections-exhausted.sh
set -euo pipefail
echo "== pool utilisation =="; psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state"
echo "== longest running =="; psql -c "SELECT pid, age(now(), query_start), left(query,80) FROM pg_stat_activity ORDER BY 2 DESC LIMIT 10"
echo "Next: to terminate a query, run scripts/kill-query.sh <pid> (logs to audit trail)"
```

Start by automating diagnosis, which is safe. Automate *action* only once the diagnosis step has been right many times.

### 2. Guard Auto-Remediation with a Circuit Breaker
Auto-restart, auto-scale, and auto-failover all share one failure mode: the remediation is triggered by a symptom whose cause the remediation does not fix, so it fires forever. A restart loop turns a degraded service into a total outage and destroys the evidence you needed.

Every automated action needs four guards:

- **Rate limit** — at most N actions per window, per target.
- **Circuit breaker** — after N failed attempts, stop and page a human. Do not retry.
- **Blast radius cap** — never act on more than a fraction of instances at once.
- **Preconditions** — verify the state that justifies the action still holds, immediately before acting.

```
if utilisation > 90% for 5m
   and actions_last_hour < 3
   and healthy_replicas >= 2
   and not incident_freeze_active:
       scale_out(step=1); log(action, actor="autoscaler", reason, before, after)
else:
       page("autoscale precondition failed", context)
```

### 3. Route and Deduplicate Alerts
Route by service ownership, not by a single catch-all channel; a page nobody owns is a page everybody ignores. Then reduce volume before it reaches a human:

- **Deduplicate** on a stable fingerprint (alert name + service + instance), so 400 firing pods send one page.
- **Group** related alerts into one notification with a short delay.
- **Inhibit** the downstream alerts when the upstream cause is already firing — no `api-errors` page when `database-down` is active.
- **Suppress** during known maintenance windows, with an expiry so the silence cannot outlive the work.

### 4. Automate Incident Setup
The first five minutes of an incident are almost entirely clerical. Do them in one command: create the channel, open the incident record, invite the on-call and the service owner, post the runbook link and current dashboards, start the timeline, and set the status page to investigating. The responder should arrive to a workspace that already exists.

Feed every subsequent automated action back into the same timeline, so the record for `incident-timeline-creation` accumulates for free instead of being reconstructed later.

### 5. Use ChatOps for Shared Context
Running commands from the incident channel makes each action visible, attributed, and timestamped for everyone — including the people who join at minute 40. Restrict the destructive verbs to a role, require an explicit confirmation for them, and echo the full command and its result back into the channel.

### 6. Pick Targets by Measuring Toil
Automate what actually costs you, not what is fun to automate. Track per alert: page count, minutes spent, how often the response was identical, and whether the fix was reversible. The best candidates are frequent, mechanical, and safe. A rare page requiring judgement should get a better runbook, not a robot.

### 7. Make Every Action Logged and Reversible
Each automated action records who or what triggered it, why, what changed, the state before and after, and how to undo it. If an action cannot be undone — deleting data, rotating a credential others depend on — it needs a human approval step regardless of how confident the automation is.

## Warning Signs

- Auto-remediation with no attempt counter, no circuit breaker, no cap
- Restarts that hide a recurring fault, so nobody sees the underlying trend
- One alert channel for every service, and nobody reads it
- Alert storms where one root cause pages twenty times
- Automated actions that appear in no log and no timeline
- Silences with no expiry, quietly muting a real alert for months
- Automation running with standing admin credentials
- Runbook scripts that have never been executed outside an incident
