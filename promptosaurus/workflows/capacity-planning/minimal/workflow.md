---
name: "capacity-planning"
description: "Forecast resource needs and plan infrastructure scaling"
version: "1.0"
languages: ["sql", "python"]
subagents: ["observability/metrics", "orchestrator"]
---

# Capacity Planning Workflow (Minimal)

## Purpose
Forecast future resource needs based on growth trends and plan infrastructure scaling to support business growth without running out of capacity.

## Steps

### 1. Analyze Current Capacity
- Document current infrastructure (servers, CPU, memory, disk, network)
- Measure current usage (CPU%, memory%, disk usage, throughput)
- Identify bottlenecks (what's running close to limits?)
- Document growth history (how did we get here?)

### 2. Forecast Future Demand
- Review business growth projections (2x, 5x in 12 months?)
- Analyze usage trends (growing at 2% monthly, doubling annually?)
- Project peak loads (Black Friday 10x normal traffic?)
- Model growth curves (linear, exponential, seasonal)

### 3. Identify Constraints
- What will hit limits first? (CPU? Disk? Memory? Network?)
- How much headroom before problem occurs? (90% full → problem?)
- Lead time to acquire new capacity (1 month? 3 months?)
- Cost vs. performance tradeoff

### 4. Plan Scaling Strategy
- Vertical scaling: Add CPU/memory to existing servers
- Horizontal scaling: Add more servers
- Autoscaling: Dynamically add/remove instances based on load
- Optimization: Reduce resource usage per request

### 5. Budget & Procurement
- Calculate cost of capacity increases
- Timeline for procurement/provisioning
- Budget approval and allocation
- Implementation plan and schedule

### 6. Implement & Monitor
- Deploy new capacity
- Verify performance meets targets
- Monitor utilization to validate forecast accuracy
- Plan next capacity increase cycle (quarterly, annually)

### 7. Review & Adjust
- Did forecast match reality?
- What changed in business projections?
- Refine forecasting model for next cycle
