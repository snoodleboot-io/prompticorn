# Kubernetes Resource Management (Minimal)

## Purpose
Size, cap, and scale workloads so pods get the CPU and memory they need without starving the node.

## Core Techniques

### 1. Set Requests and Limits
```yaml
resources:
  requests:          # what the scheduler reserves — drives placement
    cpu: 100m        # 0.1 core
    memory: 128Mi
  limits:            # the ceiling the kernel enforces
    cpu: 500m
    memory: 512Mi
```
`requests` decides which node the pod lands on. `limits` decides what happens when it misbehaves. Omit requests and the scheduler assumes zero, happily overpacking the node.

### 2. Know How CPU and Memory Limits Differ
| | Over the limit |
|---|---|
| CPU | **Throttled** — capped, stays alive, gets slow |
| Memory | **OOMKilled** — container killed immediately |

That asymmetry drives the tuning: an over-tight CPU limit produces mysterious latency, an over-tight memory limit produces restart loops.

### 3. Understand the QoS Class You Get
```
Guaranteed  requests == limits for every resource   evicted last
Burstable   requests < limits                       evicted in the middle
BestEffort  nothing set                             evicted first
```
Set `requests == limits` for latency-sensitive or stateful workloads to earn `Guaranteed`.

### 4. Autoscale on the Right Signal
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: api}
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: {type: Utilization, averageUtilization: 70}
```
HPA utilization is a percentage **of requests**, not of the node. If requests are wrong, the HPA is wrong.

### 5. Fence Off Namespaces
```yaml
apiVersion: v1
kind: ResourceQuota
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    pods: "50"
```
Add a `LimitRange` alongside it to supply defaults, so a pod that forgets its resources block doesn't land as `BestEffort`.

### 6. Size From Observed Usage
```bash
kubectl top pods --containers          # live usage
# p95 over a week beats a guess:
# quantile_over_time(0.95,
#   container_memory_working_set_bytes{pod=~"api-.*"}[7d])
```
Set requests near observed p95, limits with real headroom above it.

## Warning Signs

- `OOMKilled` in `kubectl describe pod` → memory limit too low
- High `container_cpu_cfs_throttled_seconds_total` → CPU limit too low
- Pods `Pending` with "Insufficient cpu" → requests exceed cluster capacity
- Node usage at 30% while pods won't schedule → requests inflated
- No `LimitRange` → unspecified pods evicted first under pressure
