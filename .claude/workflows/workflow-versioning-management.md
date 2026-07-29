# Workflow Versioning Management Workflow

Running several versions of a workflow at once without breaking in-flight runs,
historical reproducibility, or downstream consumers.

`workflow-migration-patterns` covers moving from one version to the next.
`workflow-rollback-strategies` covers going back. This workflow covers the rules
that make both of those possible: what a version identifies, and what changes are
safe.

---

## 1. Version the definition, the code, and the contract separately

Collapsing these into one number is why "we changed nothing" incidents happen.

| Versioned thing | Changes when | Consumers affected |
|-----------------|--------------|--------------------|
| **Definition** | Steps, graph, schedule change | In-flight runs |
| **Step implementation** | Step code or image changes | Nobody, if the contract holds |
| **Output contract** | Schema or semantics of output change | Every downstream consumer |

### Implementation:
```yaml
workflow:
  name: nightly_rollup
  definition_version: 2026.7.14-3
  output_contract: v2                 # independent of definition version
  steps:
    - id: transform
      image: registry/transform@sha256:...    # pinned by digest
```

A definition change that leaves the output contract intact is invisible downstream
and can ship freely. A contract change is a breaking change regardless of how small
the diff looks.

---

## 2. Compatibility rules

### Characteristics:
| Change | Compatibility | Safe to ship alone? |
|--------|---------------|---------------------|
| Add an optional output field | Backward compatible | Yes |
| Add a required input field | **Breaking** | No — default it first |
| Remove or rename an output field | **Breaking** | No — deprecate first |
| Change a field's type or units | **Breaking**, and silent | No — new field instead |
| Change semantics, same schema | **Breaking**, and invisible | No — version the contract |

The dangerous row is the last two. A field that keeps its name and type while
changing meaning (cents → dollars, gross → net) passes every schema check and
corrupts every consumer. **Rename on semantic change** so the break is loud.

### Implementation:
```yaml
compatibility:
  policy: backward_compatible_within_major
  breaking_change_requires: [new_major, deprecation_period, consumer_signoff]
  deprecation_period: 90d
```

---

## 3. Running versions concurrently

### Implementation Strategy:
```yaml
versions:
  - {version: 2026.7.14-3, status: active,     accepts_new_runs: true}
  - {version: 2026.7.14-2, status: draining,   accepts_new_runs: false}
  - {version: 2026.6.1,    status: retired,    retained_for: audit}
```

- A run **binds to a version at start** and keeps it for its lifetime. Swapping the
  definition under a running workflow is how in-flight state stops matching the graph.
- Keep at least one prior version deployable, or rollback is unavailable.
- Retain retired definitions for the audit period even when undeployable — you must
  be able to explain a historical run.

### Advantages & Disadvantages:
- **Advantage:** Deploys and rollbacks stop being coordinated events
- **Disadvantage:** Two active versions means two code paths to support and test
- **Disadvantage:** Version sprawl without a retirement policy

---

## 4. Schema evolution for workflow state

In-flight state serialized under an old definition must still deserialize under the
new one.

```yaml
state_schema:
  version: 4
  migrations:
    - {from: 3, to: 4, add: {region: default("global")}}   # additive, defaulted
  on_unknown_field: preserve       # never drop — a rollback needs it back
```

- **Additive with defaults** is the only change that is always safe
- **Preserve unknown fields** rather than dropping them; dropping makes rollback
  lossy and silently so
- Test deserialization of every retained state version in CI, not by hoping

---

## 5. Reproducibility

"What did this run actually execute?" must be answerable months later.

```yaml
run_record:
  definition_version: 2026.7.14-3
  definition_digest: sha256:...
  step_images: {transform: sha256:..., publish: sha256:...}
  config_digest: sha256:...
  inputs_digest: sha256:...
```

Pin by **digest, not tag**. A mutable tag means the recorded version no longer
identifies what ran, which defeats audit, rollback scoping, and data repair at once.

---

## 6. Deprecation

```yaml
deprecation:
  contract: v1
  announced: 2026-05-01
  sunset: 2026-08-01
  consumers_notified: [finance_close, exec_dashboard]
  telemetry: v1_read_count        # measure actual use before removing
```

Measure before removing. Consumer lists are always incomplete; usage telemetry on
the old contract is the only reliable evidence that nothing still depends on it.
Removing on the announced date without checking is how a "deprecated for 3 months"
field takes down a report.

---

## Best Practices

1. **Version definition, implementation, and output contract separately.**
2. **Bind a run to its version at start** and never swap underneath it.
3. **Rename on semantic change** so silent breaks become loud ones.
4. **Additive-with-defaults for state schema;** preserve unknown fields.
5. **Pin definitions and images by digest,** never by tag.
6. **Keep one prior version deployable** so rollback stays available.
7. **Retain retired definitions** for the audit period.
8. **Measure usage before sunsetting** a deprecated contract.

---

## Common Pitfalls

- **One version number for everything.** A harmless step change looks like a
  breaking contract change, so nobody trusts the number.
- **Changing units or meaning without renaming.** Passes schema validation,
  corrupts every consumer.
- **Swapping the definition under in-flight runs.** State no longer matches the graph.
- **Dropping unknown state fields.** Rollback becomes lossy, silently.
- **Mutable image tags.** The recorded version does not identify what ran.
- **Retaining only the current version.** No rollback, no historical explanation.
- **Sunsetting on schedule without usage telemetry.** The consumer list was incomplete.

---

## Related Patterns

- `workflow-migration-patterns` — moving between the versions this defines
- `workflow-rollback-strategies` — restoring a prior version
- `workflow-compliance-patterns` — retention and audit obligations on old versions
- `api-versioning-strategy` — the same compatibility rules for service interfaces