---
name: "data-quality"
description: "Implement data validation, testing, and quality monitoring"
version: "1.0"
languages: ["python", "sql"]
subagents: ["data/quality", "data/pipeline", "observability/metrics"]
---

# Data Quality Workflow (Minimal)

## Purpose
Establish comprehensive data quality framework to catch issues early, prevent bad data propagation, and maintain user trust in analytics.

## Steps

### 1. Define Quality Dimensions
- **Completeness:** Are all required fields populated?
- **Accuracy:** Does data match source of truth?
- **Consistency:** Are values consistent across tables?
- **Timeliness:** Is data fresh enough for use?
- **Validity:** Do values conform to expected format/range?

### 2. Design Quality Checks
- Row-level checks (null values, data types, ranges)
- Aggregate checks (row counts, distribution anomalies)
- Referential integrity (foreign keys exist)
- Business logic validation (total = sum of parts)
- Freshness checks (data arrived on time)

### 3. Implement Testing Framework
- Use dbt tests for SQL-based validation
- Write Python/pandas quality assertions
- Create data quality gates in pipeline
- Fail pipeline if quality thresholds violated

### 4. Set Up Monitoring & Alerts
- Track quality metrics in real-time dashboards
- Alert on threshold violations (error rate >1%)
- Monitor trend (% quality declining?)
- Generate quality reports for stakeholders

### 5. Create SLAs
- Freshness SLA: Data available by 8am
- Accuracy SLA: 99.9% of records valid
- Availability SLA: 99.5% uptime
- Completeness SLA: All required fields populated

### 6. Establish Remediation Process
- Root cause analysis for failures
- Data repair procedures (backfill, correction)
- Prevention: Fix source system issues
- Documentation: Record lessons learned

### 7. Governance & Compliance
- Track data lineage and ownership
- Document quality rules and exceptions
- Audit trail for corrections
- Compliance mappings (GDPR, CCPA requirements)
