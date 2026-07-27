# Cloud Cost Optimization (Minimal)

## Purpose
Cut the cloud bill through the levers that actually move it — right-sizing,
commitment discounts, storage tiering, killing idle resources, and controlling
egress — not by micro-optimizing individual line items.

## Core Techniques

### 1. Right-Size Before Anything Else
The largest lever, and the first one. Most instances, databases, and volumes are
provisioned well above what they use, sized from a guess or a worst-case that
never arrives. Measure actual CPU, memory, and IO utilization, then match the
instance family and size to the real workload. For Kubernetes specifically, this
is requests-vs-limits tuning — see kubernetes-resource-management. Right-sizing
compounds with every other lever, so do it first.

### 2. Buy Commitment for the Steady Baseline
On-demand pricing is a premium for flexibility you may not need. For the
predictable baseline of your usage, buy committed-use discounts, savings plans,
or reserved instances (all three providers offer a version). Keep on-demand for
the spiky top of the curve, and use spot / preemptible instances for
fault-tolerant, interruptible batch work at a steep discount. The shape is:
commit the floor, burst on-demand, batch on spot.

### 3. Tier and Lifecycle Storage
Storage accumulates silently and is rarely revisited. Move cold, infrequently
accessed data to cheaper tiers (for example S3 Standard to Infrequent Access to
Glacier) with automated lifecycle policies rather than manual sweeps. Expire data
that has a natural end of life. Delete the debris: unattached volumes, forgotten
snapshots, and old machine images that bill month after month for nothing.

### 4. Kill Idle Resources
Idle resources are pure waste — full price for zero value. The usual suspects:
non-production environments running nights and weekends, unattached disks, idle
load balancers, forgotten NAT gateways, and over-provisioned databases. Schedule
automatic shutdown of dev/test outside working hours and sweep regularly for
orphans. This is often the fastest real saving because it removes cost without
touching any running workload.

### 5. Control Egress — the Bill That Surprises Teams
Data egress is the cost that blindsides teams because it is invisible in
architecture diagrams. Internet egress, cross-region transfer, and even
cross-availability-zone traffic are all metered. Co-locate chatty services in the
same zone/region, put a CDN in front of repeatedly-served content, use private
endpoints instead of routing through the public internet, and keep compute next
to its data. A cross-cloud data pipeline can cost more in egress than in compute.

### 6. Attribute Cost With Tags
You cannot optimize what you cannot attribute. Enforce a tagging policy
(team, service, environment) and produce per-owner showback so spend has a name
against it. Untagged, growing spend is where waste hides.

## Warning Signs
- Chasing small line items while every instance runs at 15% utilization
- Everything on-demand despite a large, obviously steady baseline
- Storage that only ever grows, with no lifecycle or tiering policy
- Dev and staging environments running 24/7 for a 40-hour work week
- An egress bill nobody can explain, from chatty cross-region or cross-cloud paths
- A large "untagged" bucket in the cost report that no team owns
- Reserved capacity bought once and never revisited as usage shifts
