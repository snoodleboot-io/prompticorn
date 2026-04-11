---
name: "capacity-planning-workflow"
description: "Comprehensive capacity forecasting, growth modeling, and infrastructure scaling strategy"
version: "1.0"
languages: ["sql", "python"]
subagents: ["observability/metrics", "orchestrator"]
---

# Capacity Planning Workflow (Verbose)

## Purpose
Forecast future resource needs based on growth trends, bottleneck analysis, and business projections to proactively plan infrastructure scaling and prevent capacity-related outages.

## When to Use This Workflow
- Planning infrastructure for next fiscal year
- Supporting business growth (2x, 5x projections)
- Responding to capacity-related incidents
- Optimizing cost vs. performance tradeoffs
- Planning for seasonal peaks (Black Friday, holidays)
- Consolidating or right-sizing infrastructure

## Prerequisites
- Current infrastructure inventory and utilization metrics
- Historical growth data (6-12 months minimum)
- Business growth projections from product/finance
- Understanding of peak load patterns
- Cost models for infrastructure
- Team expertise in capacity modeling

---

## Steps

### 1. Analyze Current Capacity

**Goal:** Establish baseline and identify current constraints.

#### 1.1 Infrastructure Inventory

```
API Tier:
├─ 10 c5.2xlarge instances (40 vCPU, 16GB RAM each)
├─ Total: 400 vCPU, 160GB RAM
├─ Current usage: ~60% CPU, ~45% memory
├─ Network: 100Gbps connection to load balancer

Database:
├─ 1 db.r5.4xlarge (16 vCPU, 128GB RAM)
├─ 2 read replicas (standby for failover)
├─ Storage: 500GB used of 2TB available (25%)
├─ IO: 500 IOPS average, 5000 IOPS peak

Cache (Redis):
├─ 6 nodes, 16GB each (96GB total)
├─ Current usage: ~70% memory
├─ Eviction rate: 5% (not problematic)

Storage (S3):
├─ 50TB total stored
├─ Growth: 2TB/month
├─ Retention: 7 years = 168TB projected
```

#### 1.2 Utilization Trends

```
Timeline analysis (last 12 months):

CPU Usage (API Tier):
Jan: 30%  → Jun: 50%  → Dec: 65%
Monthly growth: ~2.9% per month
Doubling time: 24 months at current rate

Memory Usage (API Tier):
Jan: 25%  → Jun: 35%  → Dec: 45%
Monthly growth: ~1.7% per month
Doubling time: 42 months at current rate

Database Connections:
Jan: 100  → Jun: 180  → Dec: 280
Monthly growth: ~11% per month
At 100% capacity in: 8 months

Disk Usage:
Jan: 200GB → Jun: 300GB → Dec: 500GB
Monthly growth: ~23GB/month
At full capacity in: 65 months (safe)
```

#### 1.3 Bottleneck Identification

```
Bottleneck Analysis:

Immediate (Next 3 months):
⚠️ Database connections approaching limit (80% at Dec)
- Max connections: 350 (r5.4xlarge limit)
- Current: 280
- Growing: 11%/month → 350 in 6 weeks
- ACTION: Increase connection pooling size NOW

Near-term (Next 6 months):
⚠️ API tier CPU approaching alert threshold (65% used)
- Target: 70% CPU max
- Current: 65%
- Growing: 2.9%/month → 70% in 2 months
- ACTION: Plan 2x API tier capacity by month 2

Medium-term (Next 12 months):
⚠️ Cache eviction increasing (5% current)
- If growth continues: 15% eviction in 6 months
- Performance impact: Increased DB queries
- ACTION: Plan cache tier expansion in month 6

No immediate concern:
✓ Database disk: 65 months remaining
✓ S3 storage: 65 months remaining
```

---

### 2. Forecast Future Demand

**Goal:** Project resource needs based on business growth.

#### 2.1 Growth Model

```
Business projections:
- Q1 2026: 10% growth YoY (seasonal)
- Q2 2026: 20% growth YoY (peak season)
- Q3 2026: 30% growth YoY (new feature launch)
- Q4 2026: 40% growth YoY (holiday sales)

Growth scenarios:

Conservative (10% avg):
├─ Dec 2026: 1.1x current usage
├─ Dec 2027: 1.2x current usage
├─ CPU: 65% → 72% → 79%

Moderate (20% avg):
├─ Dec 2026: 1.2x current usage
├─ Dec 2027: 1.44x current usage
├─ CPU: 65% → 78% → 94%

Aggressive (40% avg):
├─ Dec 2026: 1.4x current usage
├─ Dec 2027: 1.96x current usage
├─ CPU: 65% → 91% → 127% (OVERALLOCATED!)

Most likely: Moderate (20% avg)
Recommend: Plan for moderate, be ready for aggressive
```

#### 2.2 Peak Load Modeling

```
Peak scenarios:

Daily peak:
- Normal: 100K req/sec
- Peak hour: 200K req/sec (2x)
- Black Friday: 500K req/sec (5x)

Resource impact:
                Normal      Daily Peak    Black Friday
CPU             50%         100%          250% (overload!)
Memory          30%         60%           150% (overload!)
Database conn   150         300           750 (limit=350!)
Network         50Gbps      100Gbps       250Gbps (limit=100Gbps!)

Black Friday prep needed:
- Scale API tier to 3x current (handle 5x load safely)
- Scale database to 2x (handle 2x connections)
- Scale network to 5x (handle 5x traffic)
- Pre-warm caches
- Enable request queueing/rate limiting
```

---

### 3. Identify Constraints & Lead Times

**Goal:** Understand what will limit growth and how long to acquire capacity.

#### 3.1 Constraint Matrix

```
Constraint Analysis:

Database (Current Limitation):
├─ Current max connections: 350
├─ Current usage: 280 (80%)
├─ Time to max: ~6 weeks at 11%/month growth
├─ Solution: Increase instance size (r5.8xlarge)
├─ Time to upgrade: 4 weeks (replication lag)
├─ Cost impact: $5K/month
├─ Action: Order upgrade NOW

API Tier (Secondary Limitation):
├─ Current CPU: 65%
├─ Headroom before alert: 5% (at 70% alert threshold)
├─ Time to reach threshold: 2 months
├─ Solution: Add 5 more c5.2xlarge instances
├─ Time to deploy: 2 weeks (AMI, testing, deployment)
├─ Cost impact: $2K/month
├─ Action: Order infrastructure in month 1

Cache (Tertiary):
├─ Current eviction: 5%
├─ Unacceptable eviction: 20%
├─ Time to reach: 6 months
├─ Solution: Add 6 more nodes
├─ Time to deploy: 1 week
├─ Cost impact: $1.5K/month
├─ Action: Monitor, plan for month 5

Network (Not Constrained):
├─ Current: 50Gbps actual / 100Gbps allocated
├─ Black Friday peak: 250Gbps needed
├─ Lead time for upgrade: 8 weeks (ISP provisioning)
├─ Cost: $20K one-time + $2K/month
├─ Action: Request increase NOW for holiday season
```

#### 3.2 Procurement Lead Times

```
Resource Acquisition Timeline:

Request → Approval → Procurement → Shipping → Deployment
  |          |           |            |           |
  Day 1     Day 3       Day 5       Day 15      Day 30

Typical lead times:
- Cloud instance upgrade: 1 week (immediate)
- On-premise hardware: 4-6 weeks
- ISP network upgrade: 6-8 weeks
- Data center space: 2-4 weeks
- Cooling upgrade: 4-8 weeks

Critical path for black Friday:
- Network upgrade: Order by July (8 week lead)
- Database upgrade: Order by August (4 week lead)
- API tier: Order by September (2 week lead)
- Testing & validation: Complete by October
```

---

### 4. Plan Scaling Strategy

**Goal:** Choose scaling approach matching growth and cost constraints.

#### 4.1 Scaling Options

**Vertical Scaling (Add CPU/memory to existing servers):**

Pros:
- Simple (no architecture change)
- No code changes
- Lower operational complexity

Cons:
- Single large server = single point of failure
- Maximum size limits (biggest instance available)
- Downtime during upgrade
- Cost increases exponentially (2x CPU = 2x price)

Best for:
- Database tier (always vertical within reasonable limits)
- Single-threaded applications
- Time-sensitive requirements

Example:
- From: 1 db.r5.4xlarge (16 vCPU)
- To: 1 db.r5.8xlarge (32 vCPU)
- Cost: $1.5K → $3K/month (2x)
- Impact: 2x throughput, same failure risk

**Horizontal Scaling (Add more servers):**

Pros:
- Unlimited capacity (keep adding servers)
- Built-in redundancy (failure of one = minimal impact)
- Cost scales linearly (2x servers = 2x cost)
- Can scale during running (no downtime)

Cons:
- Operational complexity (state management, coordination)
- Code changes required (stateless design)
- Network/orchestration overhead
- Load balancing complexity

Best for:
- API/application tier (stateless)
- Cache layer (consistent hashing)
- Stateless services (functions)

Example:
- From: 10 API servers
- To: 20 API servers
- Cost: $5K → $10K/month (2x)
- Impact: 2x capacity, 0.5x failure risk

**Autoscaling (Dynamic scaling):**

Pros:
- Pay only for capacity used
- Automatic response to load
- Cost optimization
- High availability

Cons:
- Initialization delay (new instance takes 5 min to ready)
- Can't handle sudden spikes (ramp-up time)
- Requires stateless architecture
- Cold-start penalties

Best for:
- Web services with variable load
- Batch processing
- APIs with daily peaks

Example:
```
Autoscaling rules:
- Min instances: 5
- Max instances: 100
- Target CPU: 60%
- Scale up: If avg CPU > 60% for 5 min → add 5 instances
- Scale down: If avg CPU < 30% for 15 min → remove 5 instances

Cost savings:
- Baseline: 10 instances 24/7 = $5K/month
- With autoscaling: avg 7 instances = $3.5K/month (30% savings)
```

---

### 5. Budget & Procurement

#### 5.1 Cost Projection

```
12-Month Capacity Budget:

Current monthly: $20K
├─ API tier: $5K (10 instances)
├─ Database: $8K (primary + 2 replicas)
├─ Cache: $2K (6 nodes)
├─ Network: $3K
├─ Storage: $2K

Projected with growth (moderate scenario):

Month 1-3 (Phase 1: Database upgrade)
- Database upgrade: r5.4xl → r5.8xl (cost +$1.5K)
- Total: $21.5K/month

Month 4-6 (Phase 2: API tier expansion)
- Add 5 API instances (cost +$2.5K)
- Total: $24K/month

Month 7-12 (Phase 3: Cache + Reserve)
- Add cache nodes (cost +$1.5K)
- Network upgrade (cost +$2K)
- Contingency reserve: $1K
- Total: $28.5K/month → $30K/month

Annual investment:
- Months 1-3: $21.5K × 3 = $64.5K
- Months 4-6: $24K × 3 = $72K
- Months 7-12: $30K × 6 = $180K
- Total: $316.5K for year

ROI: Support 2x business growth vs. current infrastructure
```

#### 5.2 Procurement Timeline

```
Procurement schedule:

Now (October):
- [ ] Request network upgrade (8-week lead)
- [ ] Database upgrade procurement (4-week lead)
- [ ] Budget approval ($316K annual)

Month 1 (November):
- [ ] Deploy database upgrade
- [ ] Validate performance improvement
- [ ] Monitor connection pool usage

Month 2 (December):
- [ ] Black Friday peak testing with current capacity
- [ ] API tier expansion procurement
- [ ] Network upgrade arrives, testing begins

Month 3 (January):
- [ ] Deploy API tier expansion
- [ ] Finalize network upgrade
- [ ] Begin cache tier planning

...
```

---

## Common Pitfalls

- **Overprovisioning:** Plan for 10x growth but traffic grows 2x (wasted money)
- **Underprovisioning:** Capacity runs out unexpectedly (performance crisis)
- **Wrong bottleneck:** Upgrade CPU when disk is constraint
- **Ignoring growth spikes:** Plan for average, not peaks
- **Slow procurement:** Business grows faster than capacity arrives

## Success Criteria

- ✓ Can support 2-5x business growth without outage
- ✓ Peak loads handled gracefully (no overload)
- ✓ Cost grows slower than business (efficiency improves)
- ✓ Capacity planned 6+ months ahead
- ✓ Team confident in scaling timeline
- ✓ No capacity-related incident in past 12 months
