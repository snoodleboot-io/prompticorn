# Kubernetes Resource Management (Verbose)

## Core Patterns

### Requests vs Limits

Two numbers with two different audiences. `requests` talks to the **scheduler**:
it reserves capacity and decides placement. `limits` talks to the **kernel**: it
caps what the container may actually consume.

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi
```

The scheduler sums `requests` across all pods on a node and refuses to place more
than the node's allocatable capacity — regardless of real usage. This is why a
cluster can sit at 25% actual CPU and still report `Insufficient cpu`: the
requests are booked even when idle.

### CPU Throttling vs Memory OOMKill

The two resources fail in fundamentally different ways, and conflating them causes
most misconfiguration.

**CPU is compressible.** Exceed the limit and the kernel's CFS quota throttles the
process within each 100 ms period. The container survives and gets slower.

```bash
# Throttling is invisible in `kubectl top` — you must look for it:
kubectl exec api-0 -- cat /sys/fs/cgroup/cpu.stat
# nr_throttled 1841   <- periods where the container was capped
# throttled_usec 92310000
```

**Memory is incompressible.** There is no "use less memory a bit more slowly" —
exceed the limit and the cgroup OOM killer terminates the container immediately.

```bash
kubectl describe pod api-0 | grep -A3 "Last State"
#   Last State:  Terminated
#     Reason:    OOMKilled
#     Exit Code: 137
```

A practical consequence: a low CPU limit degrades latency in ways that are hard to
attribute, while a low memory limit announces itself with a restart loop. Teams
routinely over-tighten CPU limits and never realise, because nothing crashes.

Some teams deliberately omit CPU limits (keeping requests) so bursty workloads can
use idle node capacity, accepting noisy-neighbour risk in exchange. This is a real
trade-off, not an error — but it requires requests to be accurate.

### Quality of Service Classes

Kubernetes derives a QoS class from what you set, and uses it to order eviction
when a node comes under memory pressure.

| Class | Condition | Eviction order |
|---|---|---|
| `Guaranteed` | requests == limits, for cpu **and** memory, on every container | Last |
| `Burstable` | requests set, below limits | Middle |
| `BestEffort` | nothing set | First |

```yaml
# Guaranteed — for stateful or latency-critical workloads
resources:
  requests: {cpu: "1", memory: 1Gi}
  limits:   {cpu: "1", memory: 1Gi}
```

Anything that holds state, serves user-facing latency, or is painful to restart
should be `Guaranteed`. The cost is efficiency: you reserve the peak permanently.

### Horizontal Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {name: api}
spec:
  scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: api}
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: {type: Utilization, averageUtilization: 70}
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300    # resist flapping on spiky traffic
      policies: [{type: Percent, value: 50, periodSeconds: 60}]
    scaleUp:
      stabilizationWindowSeconds: 0      # scale up promptly
      policies: [{type: Percent, value: 100, periodSeconds: 30}]
```

The critical subtlety: `averageUtilization: 70` means 70% **of the CPU request**,
not of the node or the limit. With `requests: 100m`, the HPA scales when pods
average 70m — even on an idle node. Requests that are wrong make the HPA wrong in
the same direction.

Asymmetric stabilization is deliberate — scale up fast to absorb load, scale down
slowly to avoid thrashing.

### Namespace Governance

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: {name: team-quota, namespace: team-a}
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "50"
---
apiVersion: v1
kind: LimitRange
metadata: {name: defaults, namespace: team-a}
spec:
  limits:
    - type: Container
      default:        {cpu: 500m, memory: 512Mi}   # applied when limits omitted
      defaultRequest: {cpu: 100m, memory: 128Mi}   # applied when requests omitted
      max:            {cpu: "4",  memory: 8Gi}
```

Pair them. A `ResourceQuota` alone rejects any pod that omits resources once a
quota on that resource exists; the `LimitRange` supplies defaults so ordinary
manifests still apply.

### Right-Sizing From Data

Guessing produces either waste or instability. Measure first.

```promql
# Memory: p95 working set over a week
quantile_over_time(0.95,
  container_memory_working_set_bytes{namespace="prod", container="api"}[7d])

# CPU: p95 actual usage
quantile_over_time(0.95,
  rate(container_cpu_usage_seconds_total{namespace="prod", container="api"}[5m])[7d:5m])

# Waste: requested but unused
sum(kube_pod_container_resource_requests{resource="memory"})
  - sum(container_memory_working_set_bytes)
```

A workable starting rule: requests at observed p95, memory limit ~1.5× requests,
CPU limit ~2–4× requests (or unset for bursty services). Then iterate — the
Vertical Pod Autoscaler in `recommender` mode will do the arithmetic continuously
without mutating pods.

## Common Anti-Patterns

❌ **No requests at all** — pod becomes `BestEffort` and is evicted first, and the
scheduler treats it as free, overpacking the node.
✅ Always set requests; use a `LimitRange` to catch omissions.

❌ **Copying one resource block across every service** — a cron job and an API
server have nothing in common.
✅ Size each workload from its own observed usage.

❌ **Memory limit equal to observed peak** — a normal traffic spike OOMKills it.
✅ Leave real headroom above p95.

❌ **Aggressive CPU limits on latency-sensitive services** — invisible throttling
shows up as unexplained p99 latency.
✅ Watch `container_cpu_cfs_throttled_seconds_total`; relax or drop the limit.

❌ **HPA target set without checking requests** — utilization is relative to
requests, so a wrong request silently mis-tunes the autoscaler.
✅ Right-size requests first, then set the HPA target.

❌ **`maxReplicas` beyond cluster capacity** — the HPA scales, pods sit `Pending`.
✅ Bound `maxReplicas` by real capacity, or pair with a cluster autoscaler.

## Resource Management Checklist

- [ ] Every container sets CPU and memory requests
- [ ] Memory limits set with headroom above observed p95
- [ ] CPU limits set deliberately — or deliberately omitted
- [ ] Latency-critical and stateful workloads are `Guaranteed`
- [ ] Requests derived from measured p95, not guessed
- [ ] `ResourceQuota` and `LimitRange` on every team namespace
- [ ] HPA targets validated against actual requests
- [ ] `maxReplicas` fits cluster capacity or a cluster autoscaler is present
- [ ] Throttling and OOMKill alerts wired up
- [ ] Requests reviewed periodically against live usage
