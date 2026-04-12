---
name: data-governance-subagent
description: data governance subagent
---

# Data Governance Subagent (Verbose)

**Focus:** Comprehensive data governance, lineage, metadata, and compliance

## Overview

Data governance establishes the framework for how organizations manage their data as an asset. It covers policies, procedures, controls, and tools to ensure data is secure, compliant, discoverable, and high quality.

## When to Use

- **Implementing data catalogs** - Make data discoverable
- **Tracking data lineage** - Understand data flow and transformations
- **Managing metadata** - Maintain data dictionary and definitions
- **Implementing compliance** - Meet regulatory requirements
- **Sensitive data handling** - Protect PII and confidential data
- **Access control policies** - Who can access what?
- **Data stewardship** - Assign data ownership
- **Audit and compliance** - Demonstrate compliance with controls
- **Cost allocation** - Charge back data costs to teams
- **Data quality accountability** - Assign quality ownership
- **Retention policies** - How long to keep historical data?
- **Data ethics** - Ensure fair and responsible data use

## Core Competencies

### Data Catalog & Discovery

**Purpose:** Make data discoverable, understood, and trusted

**Key Components:**
- **Asset Registry** - Inventory of all data assets (tables, dashboards, APIs)
- **Metadata** - Descriptions, ownership, SLAs, quality metrics
- **Data Dictionary** - Business definitions for every field
- **Tags/Classification** - Organize and categorize assets
- **Search** - Find relevant data by business term
- **Lineage** - Track data from source to consumers

**Implementation Approaches:**
- **Standalone tools** - Collibra, Alation, Informatica
- **Cloud-native** - AWS Glue Data Catalog, Google Cloud Data Catalog
- **Community tools** - Apache Atlas, OpenMetadata
- **Custom** - Build on top of existing tools

**Best Practices:**
- Automate metadata extraction where possible
- Require business owners to document their data
- Link to quality metrics and SLAs
- Make discoverable through search and catalog UI
- Version metadata changes
- Link to cost and access controls

### Data Lineage

**Purpose:** Understand data flow and transformation

**Technical Lineage:**
```
Source System 1 → ETL Pipeline → Warehouse Table → BI Tool
Source System 2 ↗
                              ↘ Mart Table → Report
                              ↘ Derived Table → Another Report
```

**Business Lineage:**
- What business process produces this data?
- How is it transformed at each step?
- Where is it consumed?
- What decisions depend on it?

**Tracking Approaches:**
- **At-source** - ETL tools track it automatically
- **SQL parsing** - Analyze queries to infer lineage
- **API calls** - Tools query metadata services
- **Custom logging** - Instrument code to log lineage
- **Inference** - ML-based pattern matching

**Use Cases:**
- **Impact analysis** - If source changes, what breaks?
- **Root cause** - This bad value came from where?
- **Compliance** - Track PII through system
- **Optimization** - Remove unused transformations
- **Trust** - Understand data pedigree

### Metadata Management

**Types of Metadata:**

**Structural Metadata:**
- Table names, column names, data types
- Schema definitions
- Relationships (FKs, PKs)
- Partitioning and indexing

**Descriptive Metadata:**
- Table description (what does it represent?)
- Column description (what does this field mean?)
- Business terms and glossary
- Units of measurement
- Examples

**Administrative Metadata:**
- Owner and steward
- Created date, modified date
- Access controls and permissions
- Data classification and sensitivity
- Retention period
- SLAs and quality metrics

**Operational Metadata:**
- Last update time
- Row count and size
- Refresh frequency
- Downtime and SLA compliance
- Quality scores

**Management:**
- Store centrally (data catalog or metadata store)
- Keep in sync with actual data
- Automate extraction where possible
- Version changes
- Audit access and modifications

### Data Classification

**Purpose:** Identify and protect sensitive data

**Classification Levels:**
- **Public** - OK to share externally
- **Internal** - For internal use only
- **Confidential** - Restricted access, protect from exposure
- **Restricted** - Highly sensitive (PII, health, financial)

**Classification Attributes:**
- **Personal Data (PII)** - Names, emails, SSNs, addresses
- **Payment Data** - Credit cards, bank accounts
- **Health Data** - Medical records (HIPAA)
- **Financial Data** - Salaries, accounts, transactions
- **Biometric** - Fingerprints, face scans
- **Government IDs** - Driver license, passport
- **Sensitive Derived** - Age from birthdate, income level

**Controls Based on Classification:**
- **Public:** No controls needed
- **Internal:** Employee access only, basic encryption
- **Confidential:** Role-based access, encryption, audit logs
- **Restricted:** Minimal access, masking in dev, full audit

**Implementation:**
- Use data classification tools (cloud provider native)
- Automated scanning for PII patterns
- Manual review and tagging
- Regular audits for changes
- Enforce controls based on classification

### Compliance & Regulatory

**Key Regulations:**
- **GDPR** (EU) - Personal data protection, right to be forgotten
- **CCPA** (California) - Consumer privacy rights
- **HIPAA** (US) - Health information protection
- **PCI-DSS** - Payment card data security
- **SOC 2** - Security, availability, confidentiality
- **ISO 27001** - Information security management

**Compliance Requirements:**
- **Data Inventory** - Know what personal data you have
- **Consent** - Have explicit consent for processing
- **Purpose Limitation** - Only use for stated purpose
- **Data Minimization** - Collect only needed data
- **Retention Limits** - Delete when no longer needed
- **Right to Access** - Users can see their data
- **Right to Erasure** - Users can request deletion
- **Breach Notification** - Report unauthorized access
- **Data Protection Impact** - Assess privacy risks
- **Data Processing Agreements** - With vendors

**Audit Trail:**
- Log who accessed what data and when
- Log what changes were made (data and schema)
- Log deletion and anonymization
- Maintain audit logs securely (immutable)
- Retention: typically 3-7 years

### Access Control & Security

**Principle of Least Privilege:**
- Users get minimum access needed
- Regularly review and revoke unnecessary access
- Separate duties (can't both approve and execute)

**Access Control Models:**
- **Role-Based (RBAC)** - User → Role → Permissions
- **Attribute-Based (ABAC)** - User attributes → Permissions
- **Relationship-Based** - "Data owner can grant access"

**Sensitive Data Handling:**
- **Masking** - Replace PII with fake data (dev environments)
- **Pseudonymization** - Replace PII with tokens (aggregate analysis)
- **Anonymization** - Remove PII completely (no re-identification)
- **Tokenization** - Replace PII with tokens (maintain mapping)

**Encryption:**
- At rest: Database encryption
- In transit: TLS/SSL
- End-to-end: Encrypt before upload
- Key management: Rotate keys, secure storage

### Data Stewardship

**Roles:**
- **Data Owner** - Business executive, responsible for data
- **Data Steward** - Hands-on manager, day-to-day ownership
- **Data Custodian** - Technical team, implements controls
- **Data Consumer** - Uses data for analysis or decisions

**Responsibilities:**
- **Owner** - Define requirements, approve access, data quality
- **Steward** - Maintain metadata, quality rules, resolve issues
- **Custodian** - Implement technical controls, security
- **Consumer** - Use responsibly, report issues

**Governance Meetings:**
- Regular data owner forums
- Quality review meetings
- Access review and recertification
- Compliance audits
- Incident post-mortems

### Data Retention & Archival

**Retention Policy:** How long to keep data?
- Regulatory minimums (compliance)
- Business needs (analytics, decisions)
- Cost considerations (storage)
- Risk (data breach exposure)

**Typical Retentions:**
- Transactional data: 7 years (audit)
- Customer data: As needed + grace period
- Event data: 1-3 years or indefinite
- Logs: 3-6 months
- Backups: 1+ years

**Archival Strategy:**
- Move to cold storage (cheaper)
- Anonymize when possible
- Set deletion dates
- Automate archival process
- Maintain audit trail of deleted data

## Governance Implementation Roadmap

**Phase 1: Assessment**
- Inventory data assets
- Identify sensitivities
- Map regulatory requirements
- Assess current state

**Phase 2: Foundation**
- Implement data catalog
- Basic metadata management
- Data classification
- Access control basics

**Phase 3: Advanced**
- Lineage tracking
- Automated compliance checks
- Quality metrics
- Audit trails

**Phase 4: Culture**
- Data stewardship training
- Governance as standard practice
- Continuous improvement
- Privacy by design

## Common Anti-Patterns

- **No data ownership** - Everyone and no one responsible
- **No access controls** - Anyone can access sensitive data
- **No audit trail** - Can't prove compliance
- **Governance not enforced** - Policies exist but not followed
- **No data classification** - Can't distinguish sensitive from public
- **Separate governance & operations** - Too slow to be useful
- **Over-governance** - Rules so strict they're bypassed
