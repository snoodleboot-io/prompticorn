# Coverage Gap Analysis
*Analysis Date: 2026-04-10*

## Current Inventory

### Agents (15)
- **architect** - System design, architecture planning
- **ask** - Q&A, explanations
- **code** - Feature implementation
- **compliance** - SOC 2, GDPR, regulatory compliance
- **debug** - Debugging, troubleshooting
- **document** - Documentation generation
- **enforcement** - Code standards enforcement
- **explain** - Code walkthroughs, onboarding
- **migration** - Framework/dependency migrations
- **orchestrator** - Multi-step workflow coordination
- **planning** - PRD development
- **refactor** - Code structure improvements
- **review** - Code/performance/accessibility reviews
- **security** - Security reviews, threat modeling
- **test** - Test writing, coverage analysis

### Subagents (28)
Distributed across: code (6), architect (3), orchestrator (3), security (2), review (3), debug (3), refactor (1), migration (1), compliance (2), planning (1), others...

### Workflows (21)
accessibility, boilerplate, code, data-model, decision-log, dependency-upgrade, docs, feature, house-style, log-analysis, meta, migration, performance, refactor, review, root-cause, scaffold, strategy, strategy-for-applications, task-breakdown, testing

### Skills (8)
data-model-discovery, feature-planning, incremental-implementation, mermaid-erd-creation, post-implementation-checklist, test-aaa-structure, test-coverage-categories, test-mocking-rules

### Supported Languages (29)
c, clojure, cpp, csharp, dart, elixir, elm, fsharp, golang, groovy, haskell, html, java, javascript, julia, kotlin, lua, objc, php, python, r, ruby, rust, scala, shell, sql, swift, terraform, typescript

---

## Gap Analysis by Perspective

### 🚀 DevOps / Platform Engineering

**Current Coverage:** ✅ Good
- orchestrator/devops subagent
- dependency-upgrade workflow
- terraform conventions

**Missing:**
1. **Agent: `infrastructure`** - IaC specialist
   - Subagents: terraform, kubernetes, docker, helm, argocd, pulumi
   - Skills: infrastructure-as-code-patterns, container-best-practices, k8s-manifest-validation
   
2. **Agent: `ci-cd`** - Pipeline specialist
   - Subagents: github-actions, gitlab-ci, jenkins, buildkite, circleci
   - Skills: pipeline-optimization, caching-strategies, parallel-execution
   
3. **Workflows:**
   - `disaster-recovery-workflow` - DR planning and runbooks
   - `deployment-workflow` - Blue/green, canary, rollback strategies
   - `infrastructure-workflow` - IaC creation and management
   - `secrets-management-workflow` - Vault, SOPS, sealed secrets
   
4. **Languages:**
   - **HCL** (Terraform configuration language) - Currently only have "terraform" as general conventions
   - **Jsonnet** (K8s configuration language)
   - **Dhall** (Configuration language)

---

### 📊 SRE / Observability

**Current Coverage:** ⚠️ Limited
- debug/log-analysis subagent
- performance-workflow

**Missing:**
1. **Agent: `observability`** - Monitoring and alerting specialist
   - Subagents: metrics, logging, tracing, alerting, dashboards
   - Skills: slo-sli-definition, alert-tuning, distributed-tracing-patterns
   
2. **Agent: `incident`** - Incident management specialist
   - Subagents: triage, postmortem, runbook, oncall
   - Skills: incident-timeline-creation, root-cause-five-whys, blameless-postmortem
   
3. **Workflows:**
   - `observability-workflow` - Setup monitoring stack
   - `incident-response-workflow` - Triage, escalation, communication
   - `postmortem-workflow` - Incident analysis and learning
   - `runbook-workflow` - Operational procedure creation
   - `capacity-planning-workflow` - Resource forecasting
   - `slo-sli-workflow` - SLO/SLI definition and tracking
   
4. **Skills:**
   - `prometheus-query-patterns` - PromQL best practices
   - `grafana-dashboard-design` - Effective visualization
   - `distributed-tracing-instrumentation` - OpenTelemetry patterns
   - `log-aggregation-patterns` - Structured logging best practices

---

### 🗄️ Data Engineering

**Current Coverage:** ❌ Very Limited
- sql conventions
- data-model-discovery skill

**Missing:**
1. **Agent: `data`** - Data engineering specialist
   - Subagents: pipeline, warehouse, quality, governance, streaming
   - Skills: etl-patterns, data-validation, schema-evolution, partitioning-strategies
   
2. **Agent: `analytics`** - Analytics and BI specialist
   - Subagents: reporting, metrics, visualization, experimentation
   - Skills: metric-definition, ab-test-design, funnel-analysis
   
3. **Workflows:**
   - `data-pipeline-workflow` - ETL/ELT pipeline design
   - `data-quality-workflow` - Validation and monitoring
   - `data-governance-workflow` - Lineage, catalog, compliance
   - `schema-migration-workflow` - Database schema evolution
   - `streaming-workflow` - Real-time data processing
   
4. **Skills:**
   - `sql-optimization` - Query performance tuning
   - `dimensional-modeling` - Star/snowflake schema design
   - `data-partitioning` - Partitioning strategies for scale
   - `idempotency-patterns` - Safe retry mechanisms
   - `slowly-changing-dimensions` - SCD type 1/2/3 patterns
   
5. **Languages:**
   - **SQL dialects:** PostgreSQL, MySQL, BigQuery, Snowflake, Redshift (currently generic SQL)
   - **dbt** (data build tool configuration)
   - **Apache Spark** (PySpark, Scala)
   - **Airflow** (DAG definition)

---

### 📱 Product / Feature Development

**Current Coverage:** ✅ Good
- planning agent
- feature-workflow
- strategy workflows

**Missing:**
1. **Agent: `product`** - Product management specialist
   - Subagents: discovery, prioritization, metrics, experiments
   - Skills: user-story-writing, acceptance-criteria, feature-flagging
   
2. **Workflows:**
   - `feature-flag-workflow` - Feature toggle patterns
   - `ab-test-workflow` - Experiment design and analysis
   - `product-analytics-workflow` - Event tracking setup
   - `user-research-workflow` - Research synthesis
   
3. **Skills:**
   - `jobs-to-be-done-framework` - JTBD analysis
   - `story-mapping` - User story mapping
   - `kano-model` - Feature prioritization
   - `event-tracking-design` - Analytics instrumentation

---

### 💻 Software Engineering

**Current Coverage:** ✅ Excellent
- Most core development workflows covered

**Missing:**
1. **Agent: `api`** - API design specialist
   - Subagents: rest, graphql, grpc, websocket, openapi
   - Skills: api-versioning, pagination-patterns, rate-limiting, idempotency
   
2. **Workflows:**
   - `api-design-workflow` - RESTful/GraphQL API design
   - `api-documentation-workflow` - OpenAPI/AsyncAPI generation
   - `database-optimization-workflow` - Index design, query tuning
   - `caching-workflow` - Cache strategy and invalidation
   
3. **Skills:**
   - `rest-api-conventions` - REST best practices
   - `graphql-schema-design` - GraphQL patterns
   - `database-indexing-strategies` - Index optimization
   - `eventual-consistency-patterns` - Distributed systems

---

### 🔐 Security (Enhanced)

**Current Coverage:** ✅ Good (security agent exists)

**Missing:**
1. **Subagents:**
   - `appsec` - Application security
   - `infrastructure-security` - Cloud security, IaC scanning
   - `secrets-scanning` - Secret detection and rotation
   
2. **Workflows:**
   - `threat-modeling-workflow` (exists but check coverage)
   - `security-scanning-workflow` - SAST/DAST/SCA setup
   - `vulnerability-management-workflow` - CVE tracking and patching
   - `security-hardening-workflow` - Baseline security configs
   
3. **Skills:**
   - `owasp-top-10-patterns` - Common vulnerability prevention
   - `least-privilege-design` - IAM best practices
   - `supply-chain-security` - Dependency security

---

### 🧪 Testing (Enhanced)

**Current Coverage:** ✅ Good (test agent exists)

**Missing:**
1. **Workflows:**
   - `contract-testing-workflow` - API contract testing (Pact, Spring Cloud Contract)
   - `chaos-engineering-workflow` - Resilience testing
   - `load-testing-workflow` - Performance testing setup
   - `visual-regression-workflow` - Screenshot comparison testing
   
2. **Skills:**
   - `property-based-testing` - Hypothesis, fast-check patterns
   - `test-data-generation` - Realistic test data creation
   - `flaky-test-detection` - Identifying and fixing flakes

---

## Priority Recommendations

### 🔥 High Priority (Critical Gaps)

1. **Data Engineering Support** - Completely missing, growing need
   - Add `data` agent with pipeline/warehouse/quality subagents
   - Add data-pipeline-workflow, data-quality-workflow
   - Add SQL dialect conventions (BigQuery, Snowflake, PostgreSQL)
   - Add dbt language support

2. **SRE/Observability** - Critical for production systems
   - Add `observability` agent with metrics/logging/tracing subagents
   - Add `incident` agent with postmortem/runbook subagents
   - Add observability-workflow, incident-response-workflow, postmortem-workflow
   - Add prometheus-query-patterns, distributed-tracing skills

3. **Infrastructure as Code** - Essential for modern DevOps
   - Add `infrastructure` agent with terraform/k8s/docker subagents
   - Add infrastructure-workflow, deployment-workflow
   - Add HCL language support (Terraform-specific)

### 🎯 Medium Priority (Nice to Have)

4. **API Design Specialist**
   - Add `api` agent with rest/graphql/grpc subagents
   - Add api-design-workflow, api-documentation-workflow

5. **CI/CD Enhancement**
   - Add `ci-cd` agent with github-actions/gitlab-ci subagents
   - Add deployment-workflow, pipeline-optimization skills

6. **Enhanced Testing**
   - Add contract-testing-workflow, chaos-engineering-workflow
   - Add property-based-testing, test-data-generation skills

### 🌟 Low Priority (Future Enhancement)

7. **Product Management**
   - Add `product` agent with discovery/prioritization subagents
   - Add ab-test-workflow, feature-flag-workflow

8. **Advanced Languages**
   - SQL dialects (BigQuery, Snowflake, Redshift)
   - dbt, Airflow, Jsonnet, Dhall

---

## Implementation Roadmap

### Phase 1: Data & SRE Foundations (2-3 weeks)
- `data` agent (5 subagents)
- `observability` agent (5 subagents)
- `incident` agent (4 subagents)
- 8 new workflows (data-pipeline, data-quality, observability, incident-response, postmortem, runbook, slo-sli, capacity-planning)
- 6 new skills (sql-optimization, dimensional-modeling, prometheus-query-patterns, distributed-tracing, slo-sli-definition, incident-timeline)
- SQL dialect conventions (PostgreSQL, BigQuery, Snowflake)
- dbt language support

### Phase 2: Infrastructure & DevOps (1-2 weeks)
- `infrastructure` agent (5 subagents)
- `ci-cd` agent (5 subagents)
- 4 new workflows (infrastructure, deployment, disaster-recovery, secrets-management)
- 4 new skills (infrastructure-as-code-patterns, container-best-practices, k8s-manifest-validation, pipeline-optimization)
- HCL language support

### Phase 3: API & Testing Enhancements (1 week)
- `api` agent (5 subagents)
- 6 new workflows (api-design, api-documentation, contract-testing, chaos-engineering, load-testing, caching)
- 5 new skills (rest-api-conventions, graphql-schema-design, property-based-testing, test-data-generation, idempotency-patterns)

### Phase 4: Product & Advanced Features (1 week)
- `product` agent (4 subagents)
- 4 new workflows (ab-test, feature-flag, product-analytics, user-research)
- 3 new skills (jobs-to-be-done, story-mapping, event-tracking-design)

---

## Total Gap Summary

**New Agents Needed:** 7
- data, observability, incident, infrastructure, ci-cd, api, product

**New Subagents Needed:** ~38
- Distributed across the 7 new agents

**New Workflows Needed:** 26
- data-pipeline, data-quality, data-governance, schema-migration, streaming, observability, incident-response, postmortem, runbook, capacity-planning, slo-sli, infrastructure, deployment, disaster-recovery, secrets-management, api-design, api-documentation, contract-testing, chaos-engineering, load-testing, caching, database-optimization, ab-test, feature-flag, product-analytics, user-research

**New Skills Needed:** 25+
- SQL-related: sql-optimization, dimensional-modeling, data-partitioning, idempotency-patterns, slowly-changing-dimensions
- SRE: prometheus-query-patterns, grafana-dashboard-design, distributed-tracing-instrumentation, log-aggregation-patterns, slo-sli-definition, incident-timeline-creation
- DevOps: infrastructure-as-code-patterns, container-best-practices, k8s-manifest-validation, pipeline-optimization, caching-strategies
- API: rest-api-conventions, graphql-schema-design, database-indexing-strategies, eventual-consistency-patterns
- Testing: property-based-testing, test-data-generation, flaky-test-detection
- Product: jobs-to-be-done, story-mapping, event-tracking-design

**New Language Support:** 6+
- HCL (Terraform), dbt, Airflow, Jsonnet, Dhall
- SQL dialects (PostgreSQL, BigQuery, Snowflake, Redshift)

---

## Business Impact

### High-Value Additions
1. **Data Engineering** - Critical for data-driven companies, ML/AI workloads
2. **SRE/Observability** - Essential for production reliability, reduces MTTR
3. **Infrastructure** - Enables modern cloud-native development

### ROI Considerations
- Data pipeline automation can save 10-20 hours/week for data teams
- Incident response workflows can reduce MTTR by 30-50%
- Infrastructure workflows can reduce provisioning time by 70%
- API design workflows improve integration quality, reduce rework

### User Segments
- **Data Teams:** Immediate value from data agent
- **SRE Teams:** Immediate value from observability/incident agents
- **Platform Teams:** Immediate value from infrastructure/ci-cd agents
- **Backend Teams:** Immediate value from api agent
- **Product Teams:** Value from product agent

---

## Conclusion

Current coverage is **excellent for core software development** but has significant gaps in:
1. ❌ **Data Engineering** (critical gap)
2. ⚠️ **SRE/Observability** (limited coverage)
3. ⚠️ **Infrastructure** (basic coverage exists but needs expansion)

**Recommended Action:** Prioritize Phase 1 (Data & SRE) to close the most critical gaps affecting modern engineering teams.
