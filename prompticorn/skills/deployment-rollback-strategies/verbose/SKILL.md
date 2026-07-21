# Deployment Rollback Strategies (Verbose)

## Core Patterns

### Choosing a Strategy

The relevant axis is not "how do we deploy" but "how fast and how cheaply can we
undo". Everything else follows from that.

| Strategy | Rollback time | Extra capacity | Blast radius | Two versions live |
|---|---|---|---|---|
| Recreate | Minutes + downtime | 0 | 100% | No |
| Rolling | 3–10 min | ~1 pod | Grows with rollout | Yes, transiently |
| Blue-green | Seconds | 100% during cutover | 100%, briefly | Yes, both full |
| Canary | Seconds | 5–10% | 1–5% of users | Yes, extended |

Rolling is the sensible default: no extra infrastructure, and rollback is a
re-deploy of the previous revision. Its weakness is that reversal takes as long as
a deployment, and during a rollout you have a mixed fleet whether you wanted one or
not.

Blue-green buys near-instant reversal because rollback is a router change, not a
workload change. You pay double capacity for the duration of the cutover, and every
user moves at once — so a failure that the smoke tests missed hits everyone before
you flip back.

Canary buys the smallest blast radius and, more importantly, real production signal
before full exposure. The costs are real: two versions coexist for an extended
period, so the code must tolerate mixed-version traffic — shared caches, message
formats, and database schema all have to satisfy both.

### Blue-Green

```bash
# Deploy green alongside the live blue stack
kubectl apply -f k8s/deployment-green.yaml
kubectl rollout status deployment/api-green --timeout=300s

# Verify against green directly, before it takes user traffic
curl -fsS http://api-green.internal/healthz
./scripts/smoke-test.sh http://api-green.internal

# Cut over: one selector change
kubectl patch service api --type=json \
  -p '[{"op": "replace", "path": "/spec/selector/version", "value": "green"}]'

# Rollback is the same command in reverse — seconds
kubectl patch service api --type=json \
  -p '[{"op": "replace", "path": "/spec/selector/version", "value": "blue"}]'
```

Keep blue running and warm for at least one full traffic cycle after cutover —
typically 30–60 minutes, longer if your peak is diurnal. Tearing it down
immediately converts a two-second rollback back into a full deployment.

The subtlety people miss is connection state. A selector flip does not close
established connections; long-lived ones drain on their own schedule. If clients
hold connections for minutes, budget for that when reasoning about "instant".

### Canary With Automated Analysis

A canary whose promotion depends on a human reading a dashboard is a rolling deploy
with extra steps. The value is in binding promotion to measured signals and making
abort automatic.

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: api
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  progressDeadlineSeconds: 600
  analysis:
    interval: 60s
    threshold: 5          # consecutive metric failures before rollback
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 500        # p99 ms
        interval: 1m
    webhooks:
      - name: load-test
        url: http://flagger-loadtester/
        metadata:
          cmd: "hey -z 2m -q 20 -c 4 http://api-canary/"
```

Two statistical points determine whether this works:

**Step size must exceed your measurement floor.** At 1% of traffic on a service
doing 100 requests per second, a one-minute window gives 60 canary requests. A
0.5% regression in error rate is invisible in that sample. Either raise the initial
weight or lengthen the interval — low-traffic services often need 10% and five
minutes to say anything at all.

**Compare canary against the concurrent baseline, not against yesterday.** Traffic
mix, upstream health, and time of day all move; the only fair comparison is stable
versus canary over the same window.

A defensible progression for a moderate-traffic service: 5% for 5 minutes, 25% for
10 minutes, 50% for 10 minutes, then 100%. Rollback at any step is a traffic-weight
change back to zero.

### Feature Flags: Decoupling Deploy From Release

Deployment moves code. Release exposes behaviour. Separating them gives you a
rollback that requires no deployment at all:

```python
if flags.enabled("new-pricing-engine", user=ctx.user):
    return new_pricing(cart)
return legacy_pricing(cart)
```

Kill-switch latency is seconds and the mechanism is independent of your deployment
pipeline — which matters, because a broken release sometimes breaks the pipeline
that would have rolled it back.

Its limits are worth stating plainly:

- It only reverts behaviour that is behind a flag. A crash in startup code, a bad
  dependency upgrade, or a memory leak is unaffected.
- It does not undo side effects. If the flagged path wrote wrong values, malformed
  events, or bad cache entries, turning the flag off stops the bleeding and leaves
  the mess.
- Flags accumulate. Every flag doubles the notional test matrix. Removing a flag
  within one or two releases of full rollout should be a tracked task, not a good
  intention.

### Database Migrations: The Irreversible Part

Code rollback is a solved problem. Schema rollback is not, and schema is where
almost every "we couldn't roll back" postmortem lands.

The failure is structural. Version N+1 drops `full_name` and adds `first_name` /
`last_name`. You deploy, something else breaks, you roll code back to N — and N
selects `full_name`, which no longer exists. Every request 500s. The rollback made
things worse, and restoring from backup means losing writes since the migration.

Expand/contract removes the coupling by ensuring the live schema always satisfies
both adjacent code versions:

```sql
-- Release 1: EXPAND. Additive only. Old code unaffected.
ALTER TABLE users ADD COLUMN first_name text;
ALTER TABLE users ADD COLUMN last_name  text;

-- Release 1 (background): BACKFILL in batches, out of band.
UPDATE users
   SET first_name = split_part(full_name, ' ', 1),
       last_name  = substr(full_name, strpos(full_name, ' ') + 1)
 WHERE first_name IS NULL
   AND id BETWEEN :lo AND :hi;

-- Release 2: MIGRATE. Code writes both columns, reads the new ones.
--            Rollback to Release 1 still works — full_name is current.

-- Release 3: CONTRACT. Only once rollback past Release 2 is not a scenario.
ALTER TABLE users DROP COLUMN full_name;
```

| Phase | Reversible? | Why |
|---|---|---|
| Expand | Yes | Additive; nothing reads the new columns yet |
| Backfill | Yes | Data only, no schema or behaviour change |
| Migrate | Yes | Both column sets populated and current |
| Contract | **No** | The old column and its data are gone |

The operating rule: **never ship a schema change and the code that depends on it in
the same release.** Contract phases should lag by at least one release, and in
practice by a sprint.

Operational details that bite:

- On PostgreSQL, use `CREATE INDEX CONCURRENTLY` — a plain `CREATE INDEX` takes a
  lock that blocks writes for the duration, turning a migration into an outage.
- Backfill in bounded batches with a pause between them. A single `UPDATE` over
  50M rows holds a long transaction, bloats WAL, and blows out replica lag.
- Set a short `lock_timeout` so a migration that cannot acquire its lock fails fast
  instead of queueing behind every subsequent query.

### Rehearsing the Rollback

The rollback path executes only during emergencies. That makes it the least-tested
code you own, exercised for the first time by the person under the most pressure.
An untested rollback is a plan, not a capability.

What rehearsal reliably uncovers:

| Failure found | Typical cause |
|---|---|
| Previous image is gone | Registry lifecycle policy pruned it after 7 days |
| Old code cannot start | Config schema changed; old parser rejects new config |
| Migration will not reverse | The `down` migration was never written or never run |
| Nobody can execute it | Rollback requires an approval only one person holds |
| It takes 40 minutes | Nobody had ever measured it |

Make it routine:

- Roll back a real service in staging every sprint, end to end.
- Roll back one low-risk production deploy per month, deliberately, in business
  hours.
- Include a rollback leg in game days.
- Track time-to-rollback as a metric and treat regressions as defects.

### Keeping Rollback Fast

```bash
kubectl rollout undo deployment/api                    # previous revision
kubectl rollout undo deployment/api --to-revision=41   # a specific one
kubectl rollout status deployment/api --timeout=120s
kubectl rollout history deployment/api
```

```yaml
spec:
  revisionHistoryLimit: 10      # default is 10; do not lower it to save etcd
```

Supporting requirements: retain images for 30+ days minimum, version configuration
alongside code so a rollback reverts config too, keep the rollback command in the
runbook that on-call already has open, and make the authorisation to run it
available to whoever is on call — not to a named individual.

Define the rollback trigger *before* the deploy, in terms of your SLOs (see
`slo-sli-definition`): "roll back if error rate exceeds 1% for two minutes, or p99
exceeds 500ms for five". A pre-agreed threshold prevents the debate about whether
this is bad enough yet, which is where the minutes go. Once the system is stable,
the investigation happens with the timeline (see `incident-timeline-creation`) —
never while users are still affected.

## Common Anti-Patterns

❌ **Rollback means rebuilding from source** — a 20-minute build during an
incident, using a toolchain that may itself have moved.
✅ Roll back to a retained, immutable artifact you already ran.

❌ **Schema change and dependent code in one release** — rolling back the code
leaves it querying columns that no longer exist.
✅ Expand/contract across releases; contract lags by at least one.

❌ **Tearing down blue immediately after cutover** — you have traded a two-second
rollback for a full deployment.
✅ Keep the previous environment warm for at least one traffic cycle.

❌ **Canary promoted on human judgement** — nobody watches for the full window, and
promotion becomes a formality.
✅ Automated analysis with defined thresholds and automatic abort.

❌ **Canary weight below the measurement floor** — 1% of low traffic cannot detect
a regression in a one-minute window.
✅ Size the step and interval to produce a statistically meaningful sample.

❌ **A documented rollback procedure that has never been executed** — every latent
break in it surfaces during the incident.
✅ Rehearse on a schedule; measure the time; fix regressions.

❌ **Feature flags treated as a complete rollback mechanism** — they do not undo
bad writes, and they do not help a process that will not start.
✅ Use flags for behaviour reversal; keep artifact rollback for everything else.

❌ **Rollback gated behind a change-approval process** — the approval takes longer
than the outage it would end.
✅ Pre-authorise rollback to the last known-good version for on-call.

❌ **Aggressive image retention policies** — the artifact you need was pruned four
days ago.
✅ Retain production images at least 30 days, and pin the currently deployed digest.

## Rollback Checklist

- [ ] Deployment strategy chosen against a required rollback time, not by default
- [ ] Rollback to the previous version completes in under 5 minutes
- [ ] Previous artifacts retained ≥ 30 days and known-good digests recorded
- [ ] Configuration versioned with code so rollback reverts both
- [ ] Rollback trigger defined in SLO terms before each deploy
- [ ] Automated abort wired to error-rate and latency thresholds
- [ ] Canary step size and interval produce a meaningful sample at your traffic
- [ ] Blue-green keeps the previous environment warm post-cutover
- [ ] No schema change ships with the code that depends on it
- [ ] Every migration classified expand / backfill / migrate / contract
- [ ] Indexes built concurrently; backfills batched with a lock timeout
- [ ] Feature flags provide a kill switch for risky behaviour
- [ ] Flag removal tracked as work, not left to accumulate
- [ ] Rollback rehearsed in staging every sprint, in production monthly
- [ ] Time-to-rollback measured and trended
- [ ] On-call is pre-authorised to roll back without further approval
