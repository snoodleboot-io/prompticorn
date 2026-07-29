# Workflow Rollback Strategies Workflow

Getting back to a known-good workflow definition after a bad one ships.

Distinct from `workflow-error-handling-patterns`, which compensates for a step that
failed *inside* a run. This workflow is about the deployed definition itself being
wrong: the runs succeed, but they do the wrong thing.

---

## 1. Rollback is a property you design in, not a button

The relevant question is not "can we roll back" but **how fast, and what does it
cost**. Answer both before deploying, not during the incident.

### Characteristics:
- **Rollback window:** how long the previous version stays deployable
- **Time to restore:** detect → decide → previous version serving
- **Blast radius:** runs already started under the bad version

### Implementation:
```yaml
rollback_policy:
  retain_versions: 5
  window: 30d
  target_time_to_restore: 5m
  in_flight: drain          # drain | abort | let_finish
```

The **in-flight decision is the hard one**. Rolling the definition back does
nothing about runs already executing under the old one.

| Option | Behaviour | Use when |
|--------|-----------|----------|
| `drain` | New runs use the restored version; in-flight finish on the bad one | The bad version is wrong but not harmful |
| `abort` | Cancel in-flight runs, compensate their completed steps | Continuing causes damage |
| `let_finish` | Explicitly accept the in-flight outcomes | The bad version is merely suboptimal |

---

## 2. Versioned, immutable definitions

You cannot restore what you did not keep.

### Implementation:
```yaml
deployment:
  version: 2026.7.14-3
  immutable: true            # never edit in place; publish a new version
  previous: 2026.7.14-2
  digest: sha256:...
```

- Never mutate a deployed definition. In-place edits make "the previous version"
  unrecoverable and un-auditable.
- Pin the digest, not just the tag — a moved tag defeats the whole mechanism.
- A run records the exact version it executed under, so behaviour is explainable
  after the fact.

### Advantages & Disadvantages:
- **Advantage:** Rollback becomes a pointer change — seconds, not a rebuild
- **Advantage:** Any historical run is reproducible
- **Disadvantage:** Storage and version sprawl; needs a retention policy

---

## 3. Progressive exposure makes rollback cheap

The cheapest rollback is one where almost nothing was exposed.

### Implementation Strategy:
```yaml
rollout:
  stages:
    - {traffic: 1,   soak: 15m}
    - {traffic: 10,  soak: 1h}
    - {traffic: 50,  soak: 4h}
    - {traffic: 100}
  auto_rollback_on:
    - error_rate > 2%
    - p99_duration > 2x_baseline
    - dlq_depth_increasing
```

```
v_old ████████████████████  100% ──> 90% ──> 50% ──> 0%
v_new                        0% ──> 10% ──> 50% ──> 100%
                              ^ rollback here costs 10% of runs
```

### Use Cases:
- Any change to a workflow with side effects
- Definitions whose failure mode is data quality rather than a crash — soak long
  enough for the signal to appear

Automate the rollback trigger. A human noticing a dashboard is a slow, unreliable
detector at 3am.

---

## 4. Forward-fix vs. rollback

Rolling back is not always correct, and reflexively rolling back can make things
worse.

| Situation | Prefer |
|-----------|--------|
| Bad logic, no data written yet | **Rollback** |
| Schema already migrated forward, not backward-compatible | **Forward-fix** |
| Corrupt data already emitted | **Rollback + repair job** — the rollback alone fixes nothing |
| Cause not understood | **Rollback** — restore first, diagnose after |

The trap: rolling back the definition while leaving migrated state in place. The
old version then runs against state it does not understand — usually worse than
the bug. Keep schema changes backward-compatible for at least one version so
rollback stays available (see `workflow-versioning-management`).

---

## 5. Data repair is a separate step

A rollback restores behaviour going forward. It does not un-write what the bad
version wrote.

```yaml
remediation:
  identify: "runs WHERE version = '2026.7.14-3' AND status = 'succeeded'"
  action: reprocess_with: 2026.7.14-2
  idempotent: true
  verify: row_counts_and_checksums_match
```

- Scope the repair by the recorded version — this is why runs must record it
- Make the repair idempotent; it will be run more than once
- Verify after repairing, and report what was *not* repairable

---

## Rehearsal

An untested rollback is a hypothesis.

- Exercise rollback in a non-production environment on a schedule, not once at design time
- Measure actual time-to-restore and compare it against the target
- Rehearse the in-flight decision too — draining is where real rollbacks stall

---

## Best Practices

1. **Decide the in-flight policy before deploying,** not during the incident.
2. **Immutable, digest-pinned versions.** Never edit a deployed definition in place.
3. **Record the executed version on every run** — rollback and repair both need it.
4. **Roll out progressively with automated rollback triggers.**
5. **Keep schema changes backward-compatible for one version** so rollback stays open.
6. **Treat data repair as its own idempotent, verified step.**
7. **Rehearse on a schedule** and track measured time-to-restore.
8. **Restore first, diagnose after** when the cause is unknown.

---

## Common Pitfalls

- **Editing a deployed definition in place.** There is now no previous version.
- **Rolling back the definition but not the state.** The old version runs against
  a schema it cannot handle.
- **Forgetting in-flight runs.** They keep executing the bad version after the
  "rollback" is declared complete.
- **Assuming rollback repairs data.** It stops the bleeding; it does not undo writes.
- **Manual rollback triggers only.** Detection lags by hours.
- **Never rehearsing.** The first real attempt discovers the missing retention.
- **Retaining one version.** Two consecutive bad releases leave nothing to restore.

---

## Related Patterns

- `workflow-error-handling-patterns` — compensation for failures inside a run
- `workflow-versioning-management` — compatibility rules that keep rollback available
- `workflow-migration-patterns` — moving definitions between versions and systems
- `workflow-monitoring` — the signals that trigger an automated rollback