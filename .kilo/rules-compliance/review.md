# compliance-review.md
# Behavior when the user asks for a compliance review of code, infrastructure, or data handling.
#
# Scope: compliance requirements mapped to technical controls.
# This mode works across frameworks — always ask which one(s) apply before starting.
# Out of scope: pure security vulnerabilities without a compliance angle — use Security mode.

## Step 1 — Establish Scope

Before any review, confirm:
1. Which compliance framework(s) are in scope?
   (SOC 2, ISO 27001, GDPR, CCPA, HIPAA, PCI-DSS, FedRAMP, or other)
2. What is being reviewed? (application code, infrastructure config, data pipeline, all three)
3. Is this a gap assessment or a pre-audit readiness review?
4. Are there existing controls documented (policies, runbooks, previous audits)?

Do not proceed until the framework is confirmed — controls vary significantly.

## Framework Reference Maps

### SOC 2 (Trust Service Criteria)

CC6 — Logical and Physical Access
  - Access controls: least privilege, MFA, role-based access
  - Service accounts: no shared credentials, rotation policy
  - Offboarding: access revoked on termination

CC7 — System Operations
  - Logging: who accessed what, when, from where — retained ≥ 90 days
  - Alerting: anomalous access patterns trigger alerts
  - Change management: deploys logged, reviewed, and approved

CC8 — Change Management
  - Code review required before merge
  - Automated testing gates in CI
  - Audit trail of what was deployed and by whom

CC9 / A1 — Availability
  - Backups: automated, tested, off-site
  - RTO/RPO defined and achievable
  - Dependency on third-party services documented

### ISO 27001 (Annex A Controls)

A.8 — Asset Management
  - Data classified by sensitivity
  - Data inventory exists and is maintained
  - Retention and disposal policies enforced in code

A.9 — Access Control
  - Authentication strength matches data sensitivity
  - Access reviews conducted regularly
  - Privileged access logged separately

A.10 — Cryptography
  - Encryption at rest for sensitive data classes
  - Encryption in transit (TLS 1.2+ minimum)
  - Key management: rotation, storage, access

A.12 — Operations Security
  - Vulnerability management process
  - Capacity monitoring
  - Separation of duties for production access

A.18 — Compliance
  - Legal obligations identified per jurisdiction
  - Technical controls demonstrably meet legal requirements

### GDPR / CCPA (Privacy)

Data Minimisation
  - Only collect fields actually needed
  - Retention limits enforced (not just documented)
  - Anonymisation/pseudonymisation applied where feasible

Consent & Rights
  - Consent captured with timestamp and version
  - Right to deletion: can all data for a user be purged?
  - Right to export: can all data for a user be extracted in portable format?
  - Data subject requests: process exists and is tested

Third-Party Processors
  - All vendors who receive personal data listed
  - DPAs in place
  - Cross-border transfer mechanisms documented

Breach Notification
  - Detection capability exists (logging, alerting)
  - 72-hour notification process defined (GDPR)
  - Breach log maintained

### HIPAA (if applicable)

PHI Identification
  - All 18 PHI identifiers located in codebase and data model
  - PHI never in logs, error messages, or URLs

Technical Safeguards
  - Access controls with unique user IDs
  - Automatic logoff
  - Audit controls: who accessed PHI and when
  - Transmission security: no PHI over unencrypted channels

### PCI-DSS (if applicable)

Cardholder Data
  - PAN never stored post-authorization (unless tokenized)
  - CVV never stored at all
  - Rendering masked where displayed

Network Segmentation
  - Cardholder data environment isolated
  - Firewall rules documented and reviewed

## Reporting Format

For each finding:
- FRAMEWORK: which control or article
- CONTROL ID: e.g., CC6.1, A.9.4.2, GDPR Art.17
- LOCATION: file, config, or system component
- GAP: what is missing or insufficient
- RISK: what audit finding or regulatory consequence this creates
- REMEDIATION: specific technical action required
- EFFORT: XS / S / M / L

## End Summary

- Findings by framework and severity
- Controls that are already met (evidence that can be cited in an audit)
- Recommended remediation order based on audit risk
- Items that require policy or process changes, not just technical fixes
