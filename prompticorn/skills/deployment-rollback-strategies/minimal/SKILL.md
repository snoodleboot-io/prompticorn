# Deployment Rollback Strategies (Minimal)

## Purpose
Make "undo" a fast, boring, rehearsed operation — so shipping is cheap and a bad release costs minutes rather than an outage.

## Core Techniques

### 1. Choose a Deployment Strategy by Rollback Time
| Strategy | Rollback | Extra capacity | Blast radius on failure |
|---|---|---|---|
| Rolling | 3-10 min (re-deploy previous) | ~0 | Grows as the rollout proceeds |
| Blue-green | Seconds (flip the router back) | 100% during cutover | All users at once, briefly |
| Canary | Seconds (shift traffic to 0%) | 5-10% | 1-5% of users |

Rolling is the cheap default. Blue-green buys near-instant reversal for the price of running two full environments during the window. Canary buys the smallest blast radius and the best signal, at the price of running two versions concurrently — which your code must tolerate.

### 2. Canary With an Automated Abort
Manual canaries get promoted because someone glanced at a dashboard. Bind promotion to metrics with a defined baseline, and make abort automatic.
```yaml
analysis:
  interval: 60s
  threshold: 5          # consecutive failures before abort
  metrics:
    - name: error-rate
      thresholdRange:
        max: 1          # percent
    - name: latency-p99
      thresholdRange:
        max: 500        # ms
```
Steps of 5% -> 25% -> 50% -> 100% with a few minutes each are typical. Below roughly 1-2% of traffic, an error-rate metric has too few samples to be significant — pick a step size your traffic volume can actually measure.

### 3. Decouple Deploy From Release With Feature Flags
Shipping code and enabling behaviour are different acts. A flag kill-switch reverts behaviour in seconds without touching the deployment, and works even when the bad code is already the baseline everywhere. This is the fastest rollback available — but only for behaviour behind a flag, and it fails for anything that has already written bad data.

### 4. Database Migrations Are What Make Deploys Irreversible
A code rollback is trivial; a schema rollback is not. Once a column is dropped, the previous version's queries fail and the data is gone. Use expand/contract:

1. **Expand** — add the new nullable column. Old and new code both work.
2. **Backfill** — populate in batches, out of band.
3. **Migrate** — deploy code that writes both and reads new.
4. **Contract** — drop the old column, one or more releases later, once rollback to pre-expand is no longer a scenario.

Each phase is independently reversible because at every point the running schema satisfies both adjacent code versions. The rule: never deploy a schema change and the code that requires it in the same release.

### 5. An Untested Rollback Is Not a Rollback
The rollback path is code that runs only in emergencies — which means it is the least exercised and most likely to be broken. Exercise it deliberately: roll back a real service in staging every sprint, and roll back at least one low-risk production deploy per month. Measure the wall-clock time and treat a regression in that number as a defect.

Common discoveries: the previous image was garbage-collected, the config format changed and old code cannot parse it, the migration was not reversible, or nobody has permission to run the rollback without the one engineer who is asleep.

### 6. Keep the Previous Version Immediately Available
```bash
kubectl rollout undo deployment/api            # previous revision
kubectl rollout status deployment/api --timeout=120s
```
Keep `revisionHistoryLimit` at 10 or more, retain images for at least 30 days, and version config alongside code so rolling back the deployment rolls back its configuration too.

## Warning Signs

- No documented rollback procedure, or one that has never been run
- Rollback requires a full rebuild from source
- Schema migration and dependent code ship in the same release
- Destructive migrations with no reverse path
- Canary promotion decided by a human glancing at a graph
- Previous images or artifacts pruned within days
- Rollback needs an approval chain that takes longer than the outage
- Nobody has measured how long a rollback actually takes
