---
name: observability
description: "Design and implement comprehensive monitoring stack"
version: "1.0"
languages: ["python", "promql"]
subagents: ["observability/metrics", "observability/logging", "observability/tracing", "orchestrator"]
---

# Observability Workflow (Minimal)

## Purpose
Design and implement comprehensive monitoring, logging, and tracing infrastructure to gain visibility into system behavior and health.

## Steps

### 1. Define Observability Goals
- What systems/services need monitoring?
- What are the key health indicators?
- What failure scenarios must we detect?
- What are the SLOs/SLAs for each system?
- Who are the consumers of observability data?

### 2. Design Metrics Strategy
- Select metrics tool (Prometheus, Datadog, Grafana Cloud)
- Define key metrics (request rate, latency, errors, resource usage)
- Plan cardinality (avoid high-cardinality labels)
- Define retention policy (1 month, 1 year, raw vs aggregated)
- Plan dashboard structure (per-service, per-team, executive)

### 3. Plan Logging Infrastructure
- Choose log aggregation tool (ELK, Loki, Datadog, Splunk)
- Define log levels and sampling strategy
- Plan structured logging format (JSON with context)
- Set retention and cost targets
- Plan log indexing and queryability

### 4. Design Distributed Tracing
- Choose tracing backend (Jaeger, Zipkin, Datadog APM)
- Define sampling rate (1% of requests, or adaptive)
- Plan trace context propagation across services
- Define span attributes and naming conventions
- Plan for trace search and investigation

### 5. Set Up Alerting Rules
- Define alert thresholds (latency p95 >500ms, error rate >1%)
- Design alert routing (who gets alerted when?)
- Plan notification channels (Slack, PagerDuty, email)
- Set alert fatigue thresholds
- Create runbooks for each alert

### 6. Build Dashboards
- Service overview dashboard (health at a glance)
- Performance dashboard (latency, throughput, errors)
- Resource dashboard (CPU, memory, disk, network)
- Business metrics dashboard (users, revenue, conversions)
- Dependency map (how services interact)

### 7. Establish Runbooks
- Document how to debug each type of failure
- Create decision trees for incident response
- Include remediation steps for common issues
- Link to dashboards and logs for investigation
