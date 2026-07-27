# Disaster Recovery Planning (Minimal)

## Purpose
Define how much data loss and downtime the business can survive, then choose the cheapest recovery pattern that meets those numbers — and prove it works.

## Core Techniques

### 1. Fix RTO and RPO Before Anything Else
Two numbers drive every DR decision:
- **RTO (Recovery Time Objective)** — how long you can be *down*. "Back online within 1 hour."
- **RPO (Recovery Point Objective)** — how much *data* you can lose. "At most 5 minutes of writes."

RPO sets how often you replicate/back up. RTO sets how much standby infrastructure you keep running. They are business decisions, not engineering ones — get them from the people who own the revenue and the compliance obligations, per critical system (they differ: an order ledger and a recommendation cache are not equal).

### 2. Know Backup vs Replication vs Multi-Region
- **Backup** — periodic point-in-time copy, stored separately. Cheap, large RPO, slow restore. Recovers from *corruption and deletion* (a bad copy is a point you can go back before).
- **Replication** — continuous copy to a standby. Small RPO, but replicates corruption and bad writes *instantly* — it is not a backup.
- **Multi-region active-active** — traffic served from more than one region at once. Smallest RTO, highest cost and complexity.

You need backups even with replication: replication protects against infrastructure loss, backups protect against bad data.

### 3. Choose One of the Four DR Patterns
Ordered by increasing cost and decreasing RTO/RPO:

| Pattern | Standby state | RTO | RPO | Cost |
|---|---|---|---|---|
| Backup & restore | Nothing running; data in backups | Hours+ | Since last backup | Lowest |
| Pilot light | Core data replicated; app off | Tens of min–hours | Small | Low |
| Warm standby | Scaled-down full stack running | Minutes | Small | Medium |
| Active-active | Full stack serving in 2+ regions | Near-zero | Near-zero | Highest |

Match the pattern to the RTO/RPO you set in step 1 — don't buy active-active for a system that can tolerate an hour down.

### 4. Store Backups Out of the Blast Radius
A backup in the same account, region, or credentials as production dies with production (or with a compromised admin key). Keep copies in a separate region and a separate trust boundary; make at least one copy immutable/write-once so ransomware or a rogue actor cannot delete it.

### 5. Test the Restore, Not the Backup
A backup job reporting success proves bytes were written, not that they restore. An untested DR plan is not a plan — it is a hope with a runbook. Regularly perform a real restore into a clean environment and measure actual RTO; a failover you have never executed will surprise you on the day it matters.

## Warning Signs
- No documented RTO/RPO, or one blanket target for every system
- Replication described as "our backup" — no independent point-in-time copies
- Backups in the same region/account/credentials as production
- DR plan exists but has never been executed end-to-end
- Restore time unknown, so RTO is a guess
- Runbook naming tools/dashboards that were renamed or removed
- No immutable copy — a single deletion (or ransomware) removes every backup
