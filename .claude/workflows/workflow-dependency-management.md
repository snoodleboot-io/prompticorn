# Workflow Dependency Management Workflow

Declaring what a task needs before it can run, and deriving the execution order
from those declarations rather than hand-maintaining it.

Companion to `async-workflow-execution` (how ready tasks actually run concurrently)
and `workflow-orchestration-patterns` (how phases are shaped). This workflow is
about the graph, not the runtime.

---

## 1. The dependency graph is a DAG

Tasks are nodes; "must finish before" is a directed edge. The graph must be acyclic
— a cycle has no valid start and is a modelling error, not a scheduling problem.

### Characteristics:
- **Declare, don't order.** Each task states what it needs; the scheduler derives
  the sequence. A hand-maintained ordered list drifts the moment a task is added.
- **Edges are minimal.** Only direct dependencies; transitive ones are implied.
- **The ready set** is every task whose dependencies are all satisfied.

### Implementation:
```yaml
tasks:
  - id: fetch_schema
    depends_on: []
  - id: migrate_db
    depends_on: [fetch_schema]
  - id: build_api
    depends_on: [fetch_schema]
  - id: integration_tests
    depends_on: [migrate_db, build_api]
```

```
fetch_schema ──┬──> migrate_db ──┐
               └──> build_api ───┴──> integration_tests
```

`migrate_db` and `build_api` are independent and run concurrently. Nothing in the
declaration says so — it falls out of the graph.

### Use Cases:
- Build and deploy pipelines
- Multi-service migrations
- Any fan-out where some units feed others

### Advantages & Disadvantages:
- **Advantage:** Adding a task cannot break the ordering of unrelated tasks
- **Advantage:** Maximum safe parallelism is derived, not guessed
- **Disadvantage:** Cycles and missing nodes must be validated explicitly
- **Disadvantage:** Harder to read at a glance than a linear list — render it

---

## 2. Dependency kinds

Not every edge means the same thing, and collapsing them all into "depends_on"
serializes work that could run in parallel.

| Kind | Meaning | Blocks? |
|------|---------|---------|
| **Data** | B consumes A's output | Yes — hard edge |
| **Ordering** | B must follow A, but uses nothing from it | Yes — but often removable |
| **Resource** | A and B contend for the same lock, pool, or quota | Mutual exclusion, not ordering |
| **Soft / preferred** | B is better with A done, but can proceed | No |

### Implementation:
```yaml
- id: reindex_search
  depends_on:
    - {task: load_documents, kind: data}
  resource: {pool: search_cluster, exclusive: true}
```

Audit ordering edges regularly. Most "must run after" edges are historical
accidents, and each one removed widens the ready set.

---

## 3. Topological execution

### Implementation Strategy:
1. Validate the graph — cycles, unknown ids, unreachable tasks
2. Compute in-degree for every node
3. The ready set is every node with in-degree 0
4. Launch the whole ready set concurrently
5. On completion, decrement dependents' in-degree and re-evaluate
6. Repeat until the graph is empty or nothing is ready

```yaml
scheduling:
  mode: event_driven      # re-evaluate on each completion, not per phase
  max_concurrency: 8
```

Re-evaluate on **each completion**, not at phase boundaries. Waiting for a whole
layer to finish is the barrier anti-pattern — see `async-workflow-execution`.

---

## 4. Cycle detection and validation

Validate before executing. A cycle discovered mid-run has already done partial work.

### Implementation:
```yaml
validation:
  on_cycle: fail_fast          # report the participating tasks, not just "cycle"
  on_unknown_dependency: fail_fast
  on_orphan: warn              # unreachable task — usually a stale definition
```

Report the actual cycle path (`a → b → c → a`). "Cycle detected" without the path
is an unactionable error in a 60-node graph.

---

## 5. Failure propagation

When a task fails, its dependents cannot run. Choose the policy deliberately.

| Policy | Behaviour | Use when |
|--------|-----------|----------|
| `fail_fast` | Cancel everything in flight | Failure invalidates the whole run |
| `skip_dependents` | Mark the affected subtree skipped, let independent branches finish | Branches are independently valuable |
| `continue_all` | Only the failed task stops | Tasks are genuinely unrelated |

`skip_dependents` is usually right: an unrelated branch's work is still worth having.

```yaml
on_task_failure:
  policy: skip_dependents
  report: [failed, skipped, succeeded]
```

Report skipped tasks distinctly from failed ones. Collapsing them hides the root
cause behind a wall of secondary failures.

---

## 6. External and conditional dependencies

Not every edge points at another task.

```yaml
- id: nightly_rollup
  depends_on:
    - {external: upstream_feed, ready_when: "partition_date == today"}
    - {task: validate_inputs, kind: data}
  timeout: 2h
  on_timeout: escalate
```

- **External dependency:** a file landing, an upstream partition, a manual approval.
  Always bounded by a timeout — an unbounded external wait is a silent hang.
- **Conditional dependency:** an edge that only applies in some runs. Model it as a
  task that resolves to a no-op, not as a mutation of the graph mid-run.

Prefer **event-driven** readiness to polling where the source can notify. Poll only
when it cannot, and size the interval to how fast the state actually changes.

---

## Best Practices

1. **Declare dependencies on the task; never maintain an ordered list.**
2. **Validate the graph before running** — cycles, unknown ids, orphans.
3. **Distinguish data edges from ordering edges,** and delete ordering edges that
   no longer have a reason.
4. **Re-evaluate readiness on each completion,** not per phase.
5. **Bound every external wait** with a timeout and an escalation.
6. **Report skipped separately from failed** so the root cause stays visible.
7. **Render the graph** in the run's output — a 40-node DAG is unreadable as YAML.
8. **Keep task granularity coarse enough to be worth scheduling** and fine enough
   to expose real parallelism.

---

## Common Pitfalls

- **Hand-maintained ordering.** Adding a task silently breaks an unrelated sequence.
- **Over-declared dependencies.** "Depends on everything before it" serializes a
  graph that had real parallelism.
- **Cycles found at runtime.** Partial work is already committed by then.
- **Phase barriers instead of event-driven readiness.** One slow task stalls every
  independent branch.
- **Unbounded external waits.** The run hangs and never alerts.
- **Treating resource contention as an ordering edge.** Serializes tasks that only
  needed mutual exclusion.
- **Reporting skipped tasks as failures.** Buries the one real failure.

---

## Related Patterns

- `async-workflow-execution` — how ready tasks run concurrently
- `workflow-orchestration-patterns` — phase and gate design
- `workflow-error-handling-patterns` — what happens when a task fails
- `task-breakdown` — deciding what the tasks should be in the first place