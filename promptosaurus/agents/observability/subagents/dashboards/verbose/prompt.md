---
name: observability-dashboards-subagent
description: observability dashboards subagent
---

# Observability Dashboards Subagent (Verbose)

**Focus:** Comprehensive Grafana dashboards and visualization strategy

## Overview

Dashboards are the visual interface to your metrics. Good dashboards tell the story of system health at a glance. This subagent specializes in dashboard design, visualization selection, and dashboard governance.

## When to Use

- **Designing observability dashboards** - What should users see?
- **Creating Grafana dashboards** - Building them end-to-end
- **Visualization selection** - Choosing right chart for data
- **Dashboard organization** - Logical layout and flow
- **Dashboard templating** - Reusable dashboards
- **Mobile dashboards** - Dashboards for on-call engineers
- **Executive dashboards** - High-level business metrics
- **Operational dashboards** - Real-time system status

## Core Principles

### Dashboard Types by Audience

**SRE/Operations Dashboard:**
- Focus: System health and incidents
- Metrics: CPU, memory, disk, network, uptime
- Goal: Spot issues quickly
- Refresh: 1-5 seconds
- Interactivity: Drill down to service level

**Product/Engineering Dashboard:**
- Focus: Application performance and usage
- Metrics: Request rate, latency, errors, user activity
- Goal: Understand app behavior
- Refresh: 30-60 seconds
- Interactivity: Filter by feature, user segment

**Executive Dashboard:**
- Focus: Business and reliability metrics
- Metrics: Uptime%, Error rate, User activity, Performance
- Goal: High-level overview
- Refresh: 5 minutes
- Interactivity: Minimal, read-only

**On-Call Dashboard:**
- Focus: Critical metrics for incident response
- Metrics: Service status, error rate, latency, dependencies
- Goal: Quick assessment during incident
- Refresh: 5-10 seconds
- Interactivity: Link to runbooks, alert rules

### Visualization Types

**Time Series Graph (Most Common):**
- Best for: Trends over time
- X-axis: Time
- Y-axis: Value
- Example: CPU usage, requests/sec, latency

```
    50%|        /\
    40%|       /  \
    30%|      /    \
    20%|     /      \  /\
    10%|    /        \/  \
     0%|_______________
       13:00  14:00  15:00  16:00
```

**Stacked Area Graph:**
- Best for: Multiple series, totals
- Example: Requests by status (200, 400, 500)
- Care: Difficult to compare non-bottom series

**Bar Chart:**
- Best for: Categorical data
- Example: Error count by error code
- Note: Less good for trends (use line graph instead)

**Gauge (Radial or Linear):**
- Best for: Single current value
- Shows: Value + Min/Max + thresholds
- Example: CPU usage %, Memory usage %
- Care: Only shows current (no history)

```
          90%  100%
         /         \
        / 75°        \
       |             |
       |   CPU      |
       |    78%     |
        \           /
         \         /
          \       /
          [______|
```

**Stat (Big Number):**
- Best for: Key metric with trend
- Shows: Large number + trend arrow + change %
- Example: Uptime: 99.95% ↑ 0.3%
- Use for: Main KPIs on dashboard

**Heatmap:**
- Best for: 2D distribution
- X-axis: Time buckets
- Y-axis: Value buckets
- Color: Intensity/count
- Example: Latency distribution (darker = more common)

```
 1000ms |  . . . . . .
  100ms | . . . X X .
   10ms | . X X X X .
    1ms | X X . . . .
       +----+----+----
       13:00  14:00  15:00
```

**Percentile Graph:**
- Best for: Latency tracking (P50, P95, P99)
- Shows: Multiple percentile lines
- Example: API latency P50/P95/P99
- Use for: SLA tracking

**Table:**
- Best for: Detailed data with multiple columns
- Example: Top 10 slowest endpoints
- Interactive: Sort, filter, drill-down
- Care: Harder to spot trends

**Logs Panel:**
- Best for: Log line display
- Shows: Structured log lines
- Interactive: Filter, search, correlation
- Example: Recent errors, trace logs

**Status/Status History:**
- Best for: Up/down status over time
- Shows: Green (up) or Red (down)
- Example: Service uptime calendar
- Use for: Identifying outage patterns

### Dashboard Layout & Design

**Visual Hierarchy:**
```
┌─────────────────────────────┐
│  TITLE                      │
├─────────────────────────────┤
│  Key Metrics (P1)           │  ← Biggest, top
│  ┌─────────────┬─────────────┐
│  │             │             │
│  └─────────────┴─────────────┘
│                               │
│  Details (P2)               │  ← Smaller, lower
│  ┌──────┬──────┬──────┬──────┐
│  │      │      │      │      │
│  └──────┴──────┴──────┴──────┘
└─────────────────────────────┘
```

**Layout Best Practices:**
- Top row: Key metrics (uptime, error rate, latency)
- Middle: Detailed breakdowns (by service, by endpoint)
- Bottom: Supplementary (resource usage, dependencies)
- Left to right: Most important → least important
- Group related panels together
- Use consistent panel sizes

**Readability:**
- White space: Don't pack panels too tight
- Panel titles: Clear, 1-2 words
- Colors: Consistent meaning (red=bad, green=good)
- Thresholds: Visual (color bands showing normal/warning/critical)
- Legends: Only if multiple series

### Templating & Variables

**Problem:** Create same dashboard for all services
```
API Dashboard
API-UI Dashboard
API-Auth Dashboard
...
(many duplicates, hard to maintain)
```

**Solution: Dashboard Variables**
```
Create template: Service-Performance-Dashboard
Parameter: $service

Service: [Dropdown: api, api-ui, api-auth, ...]

Query automatically becomes:
  SELECT rate(requests{service=~"$service"})
```

**Common Variables:**
- `$service` - Select service to monitor
- `$host` - Select specific host
- `$region` - Filter by region
- `$user_segment` - Product dashboard by user type
- `$timerange` - Custom time range selector

**Implementation:**
```
1. Create query with variable: {job=~"$service"}
2. Add dropdown variable: $service
3. Set options: api, database, cache, etc
4. Dashboard filters data based on selection
5. Share single dashboard link with parameters
```

### Advanced Features

**Panel Links:**
```
Click on panel → Drill down to detail
Example:
  Top-level: Request rate by service
  Click on "api" → Details for api service
  Click on "GET /users" → Logs for that endpoint
```

**Alert Annotations:**
```
Alert fires → Annotation appears on graph
Shows timing of incidents on metrics
Helps correlate alerts with metric changes
```

**Data Source Variables:**
```
$datasource = Prometheus instance
Test with different Prometheus servers
Share dashboard, set datasource at top
```

### Mobile Dashboards

**Design for Mobile:**
- Vertical layout (one column)
- Large touch targets (easy to tap)
- Minimal text (mobile screen is small)
- Bigger fonts
- Fewer panels per screen
- Swipe between views

**Mobile Considerations:**
- Network: Lower refresh rate
- Battery: Minimal animations
- Readability: Large metrics
- Touch: No hover tooltips

### Dashboard Governance

**Naming Convention:**
```
[Team]-[Purpose]-[Scope]

Good:
  SRE-SystemHealth-All
  API-PerformanceDetails-ByEndpoint
  Product-UserActivity-Cohort
  
Bad:
  Dashboard1
  Metrics
  Important
```

**Documentation:**
```
Every dashboard needs:
- Title: Clear purpose
- Description: What it's for, who it's for
- Links: To runbooks, alerts, relevant docs
- Legend: What each color means
- Thresholds: Why these specific numbers
```

**Versioning:**
```
Store dashboard JSON in Git
Version control changes
Track who changed what and why
Easy rollback if needed

Export from Grafana → Commit to Git
Restore from Git → Import to Grafana
```

**Access Control:**
```
Public dashboards: Read-only, shared with all
Team dashboards: Read+Edit for team only
Personal dashboards: Only user can edit

Grafana teams: Restrict access by team
Folder permissions: Organize by team/app
```

### Common Mistakes to Avoid

- **Too many metrics on one dashboard** - Cognitive overload
- **No organization** - Random panels scattered
- **Missing context** - Metric with no explanation
- **Wrong visualization** - Table for trending data
- **Too low refresh rate** - Stale data, not actionable
- **Too high refresh rate** - Excessive load on Prometheus
- **No linking** - Can't drill down for details
- **No documentation** - Others don't know what it means
- **Duplicate dashboards** - When templates would work
- **Not mobile-optimized** - Can't view during incidents

### Dashboard Examples

**SRE Alert Summary Dashboard:**
```
┌─────────────────────────────────────────┐
│ Active Alerts: 2 CRITICAL, 5 WARNING   │
├─────────────────────────────────────────┤
│ Service Status (last 24h)               │
│  API: 99.95% ↑   DB: 100% ↑  Cache: 98%│
├──────────┬──────────┬────────────────────┤
│ Error    │ Latency  │ Requests/sec       │
│ Rate     │ P99      │ (by service)       │
│ 0.5%     │ 245ms    │ [Graph]            │
└──────────┴──────────┴────────────────────┘
```

**Product Performance Dashboard:**
```
┌──────────────────────────────────────────┐
│ Active Users: 42,000 ↑ 8%               │
├──────────────────────────────────────────┤
│ Requests/sec: 12,500 ↑ 2% │ Errors: 0.3% ↓
├──────┬──────┬──────┬──────┬────────────────┤
│ Top 5 Endpoints (by requests)             │
│ 1. GET /api/feed - 5,000 req/sec - 50ms  │
│ 2. POST /api/like - 3,000 req/sec - 120ms│
│ 3. POST /api/follow - 2,500 req/sec - 80ms
│ ...                                       │
├──────────────────────────────────────────┤
│ User Activity Heatmap (by hour)           │
│ [Heatmap showing peak hours]              │
└──────────────────────────────────────────┘
```

### Performance Optimization

**Dashboard Load Times:**
- Limit panels to 20 max (fewer is better)
- Use reasonable time ranges (not 1 year of data)
- Pre-aggregate data when possible
- Use recording rules for expensive queries
- Cache query results
- Refresh rate: Only as fast as needed

**Metrics Export:**
```
Example: For SLA reporting
Export: Uptime% by day
Format: CSV/JSON for reports
Frequency: Daily, weekly, monthly
```
