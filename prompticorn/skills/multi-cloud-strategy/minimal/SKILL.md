# Multi-Cloud Strategy (Minimal)

## Purpose
Decide whether to run across multiple cloud providers at all — and if so, at what
coupling level — knowing that multi-cloud usually costs more than the lock-in it
is meant to avoid.

## Core Techniques

### 1. Separate Multi-Cloud From Its Cousins
"Multi-cloud" is used for four different things; most stated needs are actually
one of the others, which are cheaper:

| Pattern | Meaning | Usual real driver |
|---|---|---|
| Multi-cloud | Same workload runs on two+ providers | Regulatory, resilience mandate |
| Best-of-breed | Different workloads on their best cloud | A genuinely superior service |
| Hybrid | Cloud plus on-prem / colo | Legacy systems, data residency |
| Multi-region | One cloud, several regions | Latency, availability, DR |

Multi-region on a single cloud solves most availability and latency goals without
paying the multi-cloud tax.

### 2. Demand a Concrete Justification
Avoiding lock-in is not, by itself, a reason. Multi-cloud is justified by specific
requirements: regulatory or data-sovereignty rules, a customer contract that
mandates it, resilience to a whole-provider outage that the business genuinely
requires, a merger/acquisition that lands you on two clouds, or one truly unique
service. If you cannot name the requirement, you are paying for a principle.

### 3. Count the Real Costs First
Duplicated expertise and tooling, a lowest-common-denominator architecture that
forfeits the best managed services, cross-cloud egress and latency, a doubled
security and identity surface, and two of every runbook. This is the price you
weigh against the lock-in you would otherwise accept.

### 4. Pick a Coupling Level Deliberately
- **Best-of-breed placement** — each workload on its strongest cloud, no
  portability requirement. Cheapest, most common, keeps managed-service leverage.
- **Portable core** — containers/Kubernetes and open data formats so a workload
  *can* move, without abstracting everything.
- **Full abstraction** — a provider-agnostic layer over everything. Maximal
  portability, but you lose the managed services that made cloud worthwhile.

Most teams that need multi-cloud want best-of-breed or a portable core, rarely
full abstraction.

### 5. Unify Identity, Secrets, and Observability
If you are genuinely multi-cloud, the cross-cutting concerns must be centralized:
federated identity, one secrets system (see secret-management), and a single pane
of glass for metrics, logs, and traces across providers. Infrastructure should be
provisioned from one IaC toolchain (see iac-best-practices), not per-cloud
consoles.

## Warning Signs
- "Multi-cloud for no lock-in" with no requirement that actually demands it
- Reaching for multi-cloud when multi-region on one cloud would meet the goal
- A lowest-common-denominator design that bans every good managed service
- Cross-cloud chatter racking up egress and latency on the hot path
- Two clouds, two IAM models, two secrets stores, and no unified view
- Failover to a second cloud that has never actually been exercised
