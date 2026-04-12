---
name: compliance-auditor-verbose
description: Comprehensive compliance framework and audit procedures
permissions:
  read:
    '*': allow
  edit:
    '*': allow
---

# Compliance Auditor (Verbose)

## Comprehensive Compliance Framework

### Introduction

Compliance auditing ensures that systems, processes, and controls meet regulatory requirements, industry standards, and security best practices. This guide provides detailed frameworks for major compliance standards including OWASP, GDPR, HIPAA, PCI-DSS, SOC 2, and ISO 27001.

## OWASP Compliance Framework

### OWASP Top 10 2021 Detailed Requirements

#### A01:2021 – Broken Access Control

**Compliance Requirements:**
1. Implement principle of least privilege
2. Deny by default for all resources
3. Enforce access controls on every request
4. Log and monitor access control failures
5. Rate limit API and controller access

**Audit Checklist:**
- [ ] Access control matrix documented
- [ ] RBAC/ABAC implemented
- [ ] Horizontal/vertical privilege checks
- [ ] Session invalidation on logout
- [ ] CORS properly configured
- [ ] Directory listing disabled
- [ ] Metadata/backup files protected

**Evidence Required:**
- Access control policy
- Role definitions and mappings
- Authorization test results
- Access control failure logs

#### A02:2021 – Cryptographic Failures

**Compliance Requirements:**
1. Classify data by sensitivity
2. Apply encryption per classification
3. Use strong, modern algorithms
4. Implement proper key management
5. Enforce HTTPS with HSTS

**Audit Checklist:**
- [ ] Data classification completed
- [ ] Encryption at rest implemented
- [ ] TLS 1.2+ enforced
- [ ] No weak ciphers (MD5, SHA1)
- [ ] Proper random generation
- [ ] Keys stored securely
- [ ] PFS enabled

**Minimum Encryption Standards:**
- AES-256 for symmetric encryption
- RSA-2048 or ECC-256 for asymmetric
- SHA-256 for hashing
- PBKDF2/bcrypt/scrypt for passwords

#### A03:2021 – Injection

**Compliance Requirements:**
1. Use parameterized queries
2. Validate all inputs
3. Escape special characters
4. Use LIMIT in SQL queries
5. Principle of least privilege for DB

**Audit Checklist:**
- [ ] Parameterized queries used
- [ ] Input validation implemented
- [ ] Stored procedures where appropriate
- [ ] ORM configured securely
- [ ] Database permissions minimal
- [ ] Code review for injection

#### A04:2021 – Insecure Design

**Compliance Requirements:**
1. Threat model for all features
2. Secure design patterns used
3. Security requirements defined
4. Security stories in backlog
5. Plausibility checks implemented

**Audit Checklist:**
- [ ] Threat models documented
- [ ] Security requirements defined
- [ ] Design reviews conducted
- [ ] Business logic tested
- [ ] Rate limiting implemented
- [ ] Resource consumption limited

#### A05:2021 – Security Misconfiguration

**Compliance Requirements:**
1. Repeatable hardening process
2. Minimal platform footprint
3. Security directives configured
4. Cloud security settings reviewed
5. Automated configuration validation

**Audit Checklist:**
- [ ] Default accounts removed
- [ ] Unnecessary features disabled
- [ ] Security headers configured
- [ ] Error handling secure
- [ ] Cloud storage secured
- [ ] Permissions reviewed

#### A06:2021 – Vulnerable and Outdated Components

**Compliance Requirements:**
1. Component inventory maintained
2. Continuous vulnerability monitoring
3. Only obtain from official sources
4. Monitor for unmaintained libraries
5. Ongoing patch management

**Audit Checklist:**
- [ ] SBOM (Software Bill of Materials)
- [ ] Dependency scanning in CI/CD
- [ ] License compliance verified
- [ ] Update process defined
- [ ] Component risk assessment
- [ ] End-of-life planning

#### A07:2021 – Identification and Authentication Failures

**Compliance Requirements:**
1. Multi-factor authentication
2. Strong password policies
3. Secure password recovery
4. Session management controls
5. Protection against enumeration

**Audit Checklist:**
- [ ] MFA implemented
- [ ] Password complexity enforced
- [ ] Account lockout configured
- [ ] Session timeout implemented
- [ ] Secure session tokens
- [ ] No default credentials

#### A08:2021 – Software and Data Integrity Failures

**Compliance Requirements:**
1. Digital signatures for software
2. Dependency verification
3. CI/CD pipeline security
4. Serialization security
5. Auto-update security

**Audit Checklist:**
- [ ] Code signing implemented
- [ ] Dependencies verified
- [ ] CI/CD access controlled
- [ ] Serialization reviewed
- [ ] Update mechanism secured
- [ ] Integrity checks implemented

#### A09:2021 – Security Logging and Monitoring Failures

**Compliance Requirements:**
1. Log security events
2. Adequate log format
3. Log integrity protection
4. Centralized log management
5. Alerting and monitoring

**Audit Checklist:**
- [ ] Login/logout logged
- [ ] Access control failures logged
- [ ] Input validation failures logged
- [ ] Log injection prevented
- [ ] Logs protected from tampering
- [ ] Monitoring configured

#### A10:2021 – Server-Side Request Forgery

**Compliance Requirements:**
1. Network segmentation
2. URL validation
3. URL schema whitelist
4. Disable HTTP redirections
5. Input validation

**Audit Checklist:**
- [ ] URL allowlist implemented
- [ ] Network segmentation verified
- [ ] Response validation
- [ ] Timeout controls
- [ ] Authentication on URLs

### OWASP ASVS Compliance Levels

**Level 1 Checklist (Minimum):**
- Basic authentication controls
- Session management
- Access control verification
- Input validation basics
- Basic cryptography
- Error handling
- Basic logging

**Level 2 Checklist (Standard):**
- All Level 1 requirements
- Advanced authentication
- Comprehensive access control
- Complete input validation
- Malicious code controls
- Business logic security
- Files and resources security
- API and web service security

**Level 3 Checklist (Advanced):**
- All Level 2 requirements
- Advanced threat resistance
- Cryptographic key management
- Advanced session management
- Malicious code resistance
- Comprehensive configuration

## GDPR Compliance Framework

### Core Principles

1. **Lawfulness, Fairness, and Transparency**
   - Clear legal basis
   - Transparent processing
   - Fair processing

2. **Purpose Limitation**
   - Specified purposes
   - Explicit purposes
   - Legitimate purposes

3. **Data Minimization**
   - Adequate data
   - Relevant data
   - Limited to necessary

4. **Accuracy**
   - Keep data accurate
   - Keep data up to date
   - Erase/rectify inaccurate data

5. **Storage Limitation**
   - Limited retention periods
   - Regular review
   - Deletion procedures

6. **Integrity and Confidentiality**
   - Technical security
   - Organizational security
   - Data breach procedures

7. **Accountability**
   - Demonstrate compliance
   - Document processing
   - Maintain records

### Data Subject Rights Implementation

**Right to Information:**
```
Required Notices:
- Identity of controller
- Contact details of DPO
- Processing purposes
- Legal basis
- Recipients
- Retention periods
- Data subject rights
- Right to complain
```

**Right of Access (Article 15):**
- Confirm processing
- Provide copy of data
- Processing information
- 30-day response time

**Right to Rectification (Article 16):**
- Correct inaccurate data
- Complete incomplete data
- Notify recipients

**Right to Erasure (Article 17):**
- Delete when no longer necessary
- Consent withdrawn
- Legal obligation
- Exceptions documented

**Right to Restriction (Article 18):**
- Accuracy contested
- Processing unlawful
- No longer needed
- Legal claims

**Right to Portability (Article 20):**
- Machine-readable format
- Commonly used format
- Direct transfer possible

**Right to Object (Article 21):**
- Direct marketing
- Legitimate interests
- Research/statistics

### Technical Implementation Requirements

**Privacy by Design:**
1. Proactive not reactive
2. Privacy as default
3. Full functionality
4. End-to-end security
5. Visibility and transparency
6. Respect for user privacy
7. Embedded into design

**Data Protection Impact Assessment (DPIA):**
- Required for high-risk processing
- Systematic description
- Necessity and proportionality
- Risk assessment
- Mitigation measures

**Breach Notification Requirements:**
- 72 hours to supervisory authority
- Without undue delay to individuals
- Document all breaches
- Breach response plan

## HIPAA Compliance Framework

### Administrative Safeguards (45 CFR 164.308)

**Security Management Process:**
1. Risk analysis (required)
2. Risk management (required)
3. Sanction policy (required)
4. Information system review (required)

**Assigned Security Responsibility:**
- Identify security official (required)
- Document responsibilities
- Report to leadership

**Workforce Security:**
1. Authorization procedures (addressable)
2. Workforce clearance (addressable)
3. Termination procedures (addressable)

**Information Access Management:**
1. Access authorization (addressable)
2. Access establishment (addressable)
3. Access modification (addressable)

**Security Awareness Training:**
1. Initial training (addressable)
2. Periodic updates (addressable)
3. Password management (addressable)
4. Protection from malware (addressable)
5. Log-in monitoring (addressable)

### Physical Safeguards (45 CFR 164.310)

**Facility Access Controls:**
1. Contingency operations (addressable)
2. Facility security plan (addressable)
3. Access control systems (addressable)
4. Maintenance records (addressable)

**Workstation Use:**
- Define proper use (required)
- Position screens appropriately
- Automatic logoff

**Workstation Security:**
- Physical safeguards (required)
- Cable locks
- Encryption

**Device and Media Controls:**
1. Disposal (required)
2. Media re-use (required)
3. Accountability (addressable)
4. Data backup (addressable)

### Technical Safeguards (45 CFR 164.312)

**Access Control:**
1. Unique user identification (required)
2. Automatic logoff (addressable)
3. Encryption/decryption (addressable)

**Audit Controls:**
- Hardware/software mechanisms (required)
- Review logs regularly
- Log retention policies

**Integrity:**
- Electronic mechanisms (addressable)
- Version control
- Change management

**Transmission Security:**
1. Integrity controls (addressable)
2. Encryption (addressable)

### HIPAA Audit Protocol

**Documentation Requirements:**
- Policies and procedures
- Risk assessments
- Training records
- Business Associate Agreements
- Incident response logs
- Access logs and reviews

## PCI-DSS v4.0 Requirements

### Build and Maintain Secure Networks

**Requirement 1: Network Security Controls**
- Network segmentation
- Firewall configuration
- DMZ implementation
- Restrict inbound/outbound traffic
- Review firewall rules bi-annually

**Requirement 2: Default Configurations**
- Change default passwords
- Remove unnecessary services
- Configure security parameters
- Encrypt administrative access
- Maintain configuration standards

### Protect Cardholder Data

**Requirement 3: Storage Protection**
- Data retention policies
- Cardholder data inventory
- Secure deletion procedures
- Encryption key management
- Mask PAN when displayed

**Requirement 4: Transmission Encryption**
- Strong cryptography
- Never send unencrypted PANs
- TLS/SSL implementation
- Wireless encryption

### Vulnerability Management Program

**Requirement 5: Anti-malware**
- Deploy on all systems
- Keep signatures current
- Active scanning
- Audit logs

**Requirement 6: Secure Development**
- Security patches within 30 days
- Secure coding guidelines
- Code reviews
- Change control processes
- Security testing

### Strong Access Control

**Requirement 7: Restrict Access**
- Need-to-know basis
- Role-based access control
- Documented approval
- Access control systems

**Requirement 8: Identify and Authenticate**
- Unique IDs for each person
- Strong authentication
- Multi-factor authentication
- Password policies
- Account lockout

**Requirement 9: Physical Access**
- Facility entry controls
- Visitor management
- Media destruction
- Device security

### Regular Monitoring and Testing

**Requirement 10: Track and Monitor**
- Log all access
- Daily log review
- Log retention (1 year)
- Time synchronization
- Secure audit trails

**Requirement 11: Security Testing**
- Quarterly vulnerability scans
- Annual penetration tests
- IDS/IPS deployment
- File integrity monitoring
- Change detection

### Information Security Policy

**Requirement 12: Security Policy**
- Formal security policy
- Risk assessment process
- Daily operational procedures
- Incident response plan
- Security awareness program

## SOC 2 Type II Audit Framework

### Trust Services Criteria

#### Security (Common Criteria)

**CC1: Control Environment**
- Integrity and ethical values
- Board oversight
- Organizational structure
- Commitment to competence
- Accountability

**CC2: Communication and Information**
- Internal communication
- External communication
- Communication methods

**CC3: Risk Assessment**
- Risk identification
- Risk analysis
- Risk management
- Fraud assessment

**CC4: Monitoring**
- Ongoing monitoring
- Separate evaluations
- Deficiency communication

**CC5: Control Activities**
- Control selection
- Technology controls
- Policy deployment

**CC6: Logical and Physical Access**
- Logical access controls
- Physical access controls
- Access provisioning
- Access reviews

**CC7: System Operations**
- Infrastructure monitoring
- Incident management
- Backup procedures
- Recovery capabilities

**CC8: Change Management**
- Change request process
- Change authorization
- Testing requirements
- Approval process

**CC9: Risk Mitigation**
- Vendor management
- Business continuity
- Risk mitigation activities

#### Availability

**A1: Availability Policy**
- Service level agreements
- Performance monitoring
- Capacity planning
- Incident response

#### Processing Integrity

**PI1: Processing Accuracy**
- Input validation
- Processing monitoring
- Output verification
- Error handling

#### Confidentiality

**C1: Confidential Information**
- Data classification
- Access restrictions
- Encryption requirements
- Disposal procedures

#### Privacy

**P1-P8: Privacy Criteria**
- Notice
- Choice and consent
- Collection
- Use and retention
- Access
- Disclosure
- Quality
- Monitoring

### Audit Evidence Collection

**System Documentation:**
- System descriptions
- Network diagrams
- Data flow diagrams
- Control matrices

**Policy Documentation:**
- Information security policy
- Access control policy
- Change management policy
- Incident response plan

**Operational Evidence:**
- Access reviews
- Change tickets
- Incident reports
- Training records
- Vulnerability scans
- Penetration tests

## ISO 27001:2022 Compliance

### Mandatory Documentation

1. Information security policy
2. Scope of the ISMS
3. Risk assessment methodology
4. Risk treatment plan
5. Statement of Applicability
6. Risk assessment results
7. Definition of security roles
8. Inventory of assets
9. Acceptable use policy
10. Access control policy
11. Operating procedures
12. Secure development policy
13. Supplier security policy
14. Incident response procedures
15. Business continuity procedures
16. Legal/regulatory requirements

### Control Categories (Annex A)

**A.5: Organizational Controls**
- 37 controls covering policies, roles, and responsibilities

**A.6: People Controls**
- 8 controls for HR security

**A.7: Physical Controls**
- 14 controls for physical security

**A.8: Technological Controls**
- 34 controls for technical security

## Audit Preparation Checklist

### Pre-Audit Activities

1. **Gap Assessment**
   - [ ] Current state analysis
   - [ ] Requirements mapping
   - [ ] Gap identification
   - [ ] Remediation plan

2. **Documentation Review**
   - [ ] Policy completeness
   - [ ] Procedure accuracy
   - [ ] Evidence collection
   - [ ] Record retention

3. **Technical Preparation**
   - [ ] Vulnerability scanning
   - [ ] Configuration review
   - [ ] Access review
   - [ ] Log analysis

4. **Team Preparation**
   - [ ] Role assignments
   - [ ] Interview preparation
   - [ ] Evidence organization
   - [ ] Communication plan

### During Audit

1. **Auditor Support**
   - Provide requested evidence
   - Facilitate interviews
   - System demonstrations
   - Clarify questions

2. **Issue Management**
   - Document findings
   - Provide context
   - Propose remediation
   - Timeline commitments

### Post-Audit

1. **Remediation**
   - Priority assignment
   - Resource allocation
   - Implementation
   - Verification

2. **Continuous Improvement**
   - Lessons learned
   - Process updates
   - Control improvements
   - Training needs

## Best Practices

1. **Maintain Compliance Continuously:** Not just for audits
2. **Automate Where Possible:** Reduce human error
3. **Document Everything:** Evidence is key
4. **Regular Self-Assessments:** Find issues early
5. **Cross-Framework Mapping:** Leverage overlap
6. **Risk-Based Approach:** Focus on high-risk areas
7. **Stakeholder Engagement:** Compliance is everyone's job
8. **Vendor Management:** Extend compliance to third parties
9. **Incident Learning:** Update controls based on incidents
10. **Stay Current:** Monitor regulatory changes