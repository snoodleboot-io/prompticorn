# Cloud Migration Strategy (Minimal)

## Purpose
Move workloads to the cloud with a per-application decision, sequenced to reduce risk — not one big-bang rewrite of everything at once.

## Core Techniques

### 1. Classify Every Workload by the 6 R's
There is no single migration; there is a decision per application. The six standard dispositions:

- **Rehost** ("lift and shift") — move as-is to cloud VMs. Fastest, lowest risk, captures none of the cloud's elasticity or managed-service savings.
- **Replatform** ("lift and reshape") — small optimizations in transit (e.g. self-managed DB → managed DB) without changing core architecture.
- **Refactor / re-architect** — redesign for cloud-native (managed services, serverless, containers). Highest cost and value; reserve for the workloads that justify it.
- **Repurchase** — drop the app and move to a SaaS equivalent.
- **Retire** — turn it off; a surprising fraction of an estate is unused.
- **Retain** — leave it where it is (too risky, not yet worth it, or compliance-bound).

Inventory first, then assign an R with a reason to each. "Retire" and "retain" decisions are as valuable as moves.

### 2. Lift-and-Shift First, Optimize After
Rehosting first gets you out of the datacenter (its lease, hardware refresh, and exit deadline) quickly and with low risk, then you optimize *in* the cloud where iteration is cheap. Trying to re-architect *during* the migration couples two hard problems — a platform change and a design change — and multiplies the risk. Migrate, stabilize, then refactor the workloads worth refactoring.

### 3. Strangle the Monolith, Don't Rewrite It
For large systems, use the **strangler-fig** pattern: put a routing layer (proxy/gateway) in front, carve out one capability at a time into the new environment, redirect that route, and repeat until the old system has nothing left and is decommissioned. Each step is small, independently shippable, and reversible — the opposite of a big-bang cutover you cannot roll back.

### 4. Treat Data Migration as the Risk
Compute is stateless and easy to move; **data is the hard part**. Large volumes take real time to copy, and the source keeps changing while you copy. Options range from bulk transfer plus change-data-capture to keep the target in sync, to database replication. Plan for consistency, validation (row counts, checksums), and the fact that transferring petabytes over the network may be slower than physical transfer appliances.

### 5. De-Risk the Cutover
The switch from old to new is where outages happen. Reduce blast radius: run old and new in parallel, cut over a slice of traffic first, keep a tested **rollback** path, and choose a low-traffic window. Never cut over a system you cannot roll back. Validate on the new environment *before* sending real users, not after.

## Warning Signs
- Big-bang plan to move everything at once with no rollback
- Re-architecting during the migration instead of after
- No workload inventory — migrating apps nobody uses (should be retired)
- Data migration treated as an afterthought vs the main risk
- Cutover with no parallel-run, canary, or rollback plan
- Every app defaulted to one R (all rehost, or all refactor)
- No validation that the target holds correct, complete data before cutover
