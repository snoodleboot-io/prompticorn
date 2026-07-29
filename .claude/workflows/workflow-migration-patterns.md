# Workflow Migration Patterns Workflow

Moving workflow definitions and their in-flight state to a new version, engine, or
platform without losing runs.

Two distinct migrations are often conflated, and they have different risks:

- **Version migration** — same engine, new definition. The hard part is in-flight runs.
- **Platform migration** — new engine (Airflow → Temporal, cron → managed service).
  The hard part is that semantics do not map one-to-one.

Companion to `workflow-versioning-management` (compatibility rules) and
`workflow-rollback-strategies` (getting back when it goes wrong).

---

## 1. Migrating in-flight runs

A definition change is easy. A run that started under the old definition and has
not finished is the actual problem.

### Characteristics:
Three viable strategies, in increasing cost and capability:

| Strategy | Behaviour | Cost |
|----------|-----------|------|
| **Drain** | Old runs finish on the old definition; new runs use the new one | Lowest — two versions coexist briefly |
| **Abort and restart** | Cancel in-flight, compensate, re-run under the new definition | Medium — only safe if steps are compensable |
| **State translation** | Map in-flight state onto the new definition and continue | Highest — needs an explicit mapping per state |

### Implementation:
```yaml
migration:
  strategy: drain
  old_version: 2026.6.1
  new_version: 2026.7.1
  drain_deadline: 48h
  on_deadline_exceeded: escalate      # never silently kill
```

**Drain is the default.** Reach for state translation only when runs are long-lived
enough that draining is not an option (multi-day or multi-week workflows).

### Advantages & Disadvantages:
- **Advantage (drain):** No mapping code, no translation bugs
- **Disadvantage (drain):** Two versions live simultaneously — both must work
- **Disadvantage (translation):** Every intermediate state needs a tested mapping;
  untested states are where data is lost

---

## 2. Expand / migrate / contract

The pattern that makes migration reversible at every step.

### Implementation Strategy:
```
1. EXPAND    Add the new field/step/queue. Old and new both work.
             Deploy. Rollback is free — nothing was removed.

2. MIGRATE   Dual-write to both. Backfill history. Verify parity.
             Reads still come from the old path.

3. SWITCH    Move reads to the new path. Keep dual-writes.
             Rollback is a read-path flip.

4. CONTRACT  Only after a full retention period with no rollback:
             stop dual-writing and remove the old path.
```

```yaml
phases:
  expand:   {deploy: new_schema_additive, reversible: true}
  migrate:  {dual_write: true, backfill: true, verify: parity_check}
  switch:   {read_from: new, dual_write: true, soak: 7d}
  contract: {remove: old_path, after: retention_window}
```

The discipline that matters: **contract is a separate deploy, much later**. Collapsing
contract into switch is what turns a reversible migration into a one-way door.

### Use Cases:
- Schema changes to workflow state or payloads
- Splitting one workflow into several, or merging several into one
- Changing a queue, topic, or storage location

---

## 3. Parallel run (shadow) verification

Before trusting the new definition, run both and compare.

```
input ──┬──> old workflow ──> output_old ──> [served]
        └──> new workflow ──> output_new ──> [compared, discarded]
                                    │
                              diff report
```

### Implementation:
```yaml
shadow:
  duration: 7d
  compare: [output_checksum, row_count, duration_p99]
  ignore: [timestamps, run_id, ordering_within_batch]
  promote_when: mismatch_rate < 0.1%
```

Define the **ignore list** deliberately. Timestamps and ids always differ; if you
do not exclude them, every run mismatches and the comparison is abandoned as noise.
Excluding too much hides real regressions.

### When to Use:
- Platform migrations, where semantic differences are expected but unknown
- Any workflow whose output feeds downstream consumers you cannot easily re-run

---

## 4. Platform migration: map semantics first

Engines differ in ways that silently change behaviour. Enumerate these before
writing any migration code.

| Semantic | Question to answer |
|----------|--------------------|
| Retry | Engine-level or step-level? Does the count reset on resume? |
| Timeout | Per step, per run, or both? What happens on breach? |
| Idempotency | Are re-deliveries possible? At-least-once or exactly-once? |
| Scheduling | How are missed windows handled — backfill, skip, or catch up? |
| Concurrency | Are overlapping runs of the same schedule allowed? |
| State | How much survives a worker restart? |

A migration that assumes matching semantics produces workflows that pass tests and
misbehave under failure — the hardest class of bug to find later.

---

## 5. Backfill

Historical runs usually need reprocessing under the new definition.

```yaml
backfill:
  range: {from: 2026-01-01, to: 2026-07-01}
  granularity: day
  max_concurrency: 4          # protect shared downstreams
  idempotent: true
  checkpoint: true            # resumable — never restart from zero
  verify: counts_and_checksums
```

- **Checkpoint it.** A backfill that must restart from the beginning after a failure
  will never finish.
- **Throttle it.** Backfills routinely take down the production dependencies they share.
- **Verify it,** and report what could not be backfilled rather than reporting success.

---

## Best Practices

1. **Separate the two migrations** — version and platform — and plan them separately.
2. **Drain by default;** translate in-flight state only for long-lived runs.
3. **Expand → migrate → switch → contract,** with contract as its own later deploy.
4. **Shadow-run before promoting,** with a deliberate ignore list.
5. **Enumerate engine semantics before porting** anything.
6. **Checkpoint, throttle, and verify every backfill.**
7. **Keep the old path deployable** until the new one has survived a full retention window.
8. **Never silently kill in-flight runs** at a drain deadline — escalate.

---

## Common Pitfalls

- **Contracting too early.** Removes the rollback path while the new one is unproven.
- **Migrating the definition and forgetting in-flight runs.** They fail mid-flight
  against a definition that no longer matches their state.
- **Assuming engine semantics match.** Retry and timeout differences surface only
  during a failure, in production.
- **Shadow comparison with no ignore list.** Everything mismatches; the signal is
  discarded as noise.
- **Unthrottled backfill.** Takes down the shared database it reads from.
- **Non-resumable backfill.** Fails at 80% and starts over.
- **Big-bang cutover.** No progressive exposure, so the blast radius is 100%.

---

## Related Patterns

- `workflow-versioning-management` — compatibility rules between versions
- `workflow-rollback-strategies` — restoring the previous version when migration fails
- `workflow-testing-patterns` — parity tests that make a shadow run trustworthy
- `workflow-dependency-management` — ordering the migration's own steps