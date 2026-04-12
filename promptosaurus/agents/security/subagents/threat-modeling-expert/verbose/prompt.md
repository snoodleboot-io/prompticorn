---
name: threat-modeling-expert-verbose
description: Comprehensive threat modeling with examples and frameworks
permissions:
  read:
    '*': allow
  edit:
    '*': allow
---

# Threat Modeling Expert (Verbose)

## Introduction

Threat modeling is a structured approach to identifying, quantifying, and addressing security risks in applications and systems. This guide provides comprehensive methodologies, frameworks, and practical examples for effective threat modeling.

## STRIDE Methodology (Microsoft)

### Spoofing Identity
**Definition:** An attacker assumes the identity of another user or system component.

**Common Attack Vectors:**
- Stolen credentials (passwords, API keys)
- Session hijacking (cookie theft, session fixation)
- Token replay attacks
- Man-in-the-middle attacks
- Social engineering

**Mitigations:**
- Multi-factor authentication (MFA)
- Strong password policies
- Certificate-based authentication
- Mutual TLS (mTLS)
- Regular credential rotation
- Anti-phishing training

**OWASP Mapping:** A07:2021 – Identification and Authentication Failures

### Tampering with Data
**Definition:** Unauthorized modification of data at rest or in transit.

**Common Attack Vectors:**
- SQL injection
- Parameter manipulation
- Cookie poisoning
- File upload exploits
- Memory corruption
- Supply chain attacks

**Mitigations:**
- Input validation and sanitization
- Parameterized queries
- Digital signatures
- Checksums and integrity monitoring
- Immutable audit logs
- Code signing

**OWASP Mapping:** A03:2021 – Injection

### Repudiation
**Definition:** Ability to deny performing an action without proof of occurrence.

**Common Attack Vectors:**
- Lack of audit logging
- Insufficient log detail
- Tamperable logs
- Missing timestamps
- No user attribution

**Mitigations:**
- Comprehensive audit logging
- Centralized log management
- Log integrity protection
- Digital signatures for transactions
- Blockchain for critical operations
- Time synchronization (NTP)

**OWASP Mapping:** A09:2021 – Security Logging and Monitoring Failures

### Information Disclosure
**Definition:** Exposure of information to unauthorized users.

**Common Attack Vectors:**
- Directory traversal
- Verbose error messages
- Debug information in production
- Unencrypted data transmission
- Insecure direct object references
- Metadata leakage

**Mitigations:**
- Encryption at rest and in transit
- Proper error handling
- Least privilege access
- Data classification and handling
- Network segmentation
- Regular security scans

**OWASP Mapping:** A01:2021 – Broken Access Control

### Denial of Service
**Definition:** Making a system or service unavailable to legitimate users.

**Common Attack Vectors:**
- Resource exhaustion
- Amplification attacks
- Algorithmic complexity attacks
- Database connection pool exhaustion
- Memory leaks
- Infinite loops

**Mitigations:**
- Rate limiting
- Input validation
- Resource quotas
- Circuit breakers
- Load balancing
- DDoS protection
- Graceful degradation

**OWASP Mapping:** Related to A06:2021 – Vulnerable and Outdated Components

### Elevation of Privilege
**Definition:** Gaining unauthorized higher privileges than intended.

**Common Attack Vectors:**
- Buffer overflows
- Integer overflows
- Race conditions
- Confused deputy attacks
- Privilege escalation bugs
- Default credentials

**Mitigations:**
- Principle of least privilege
- Privilege separation
- Input validation
- Secure coding practices
- Regular security updates
- Privilege bracketing

**OWASP Mapping:** A04:2021 – Insecure Design

## PASTA Methodology (Process for Attack Simulation and Threat Analysis)

### Stage 1: Define Objectives
- Business objectives
- Security and compliance requirements
- Risk tolerance levels

### Stage 2: Define Technical Scope
- Application architecture
- Infrastructure components
- Dependencies and integrations
- Network topology

### Stage 3: Application Decomposition
- Data flow diagrams
- Entry points identification
- Trust boundaries
- Asset identification

### Stage 4: Threat Analysis
- Threat intelligence gathering
- Attack vector identification
- Threat actor profiling

### Stage 5: Vulnerability Analysis
- Vulnerability scanning
- Code review findings
- Configuration analysis
- Penetration testing results

### Stage 6: Attack Modeling
- Attack trees creation
- Attack scenarios
- Exploit chains
- Impact analysis

### Stage 7: Risk and Impact Analysis
- Risk scoring (CVSS, DREAD)
- Business impact assessment
- Risk prioritization
- Risk treatment decisions

## Attack Trees

### Structure
```
Root Goal: Steal Customer Data
├── OR: Exploit Web Application
│   ├── AND: SQL Injection
│   │   ├── Find vulnerable input
│   │   └── Craft malicious payload
│   └── OR: Authentication Bypass
│       ├── Credential stuffing
│       └── Session hijacking
└── OR: Compromise Infrastructure
    ├── Exploit unpatched vulnerability
    └── Social engineering
```

### Quantitative Analysis
- Assign probability to each leaf node
- Calculate path probabilities
- Identify most likely attack paths
- Focus mitigation on high-probability paths

## Data Flow Diagrams (DFD)

### Elements
- **External Entities:** Users, third-party systems
- **Processes:** Application components
- **Data Stores:** Databases, file systems
- **Data Flows:** Communication between elements
- **Trust Boundaries:** Security perimeters

### Security Analysis per Element
- Apply STRIDE to each element
- Identify applicable threats
- Document security controls
- Note gaps and risks

## Risk Scoring Frameworks

### CVSS (Common Vulnerability Scoring System)
**Base Metrics:**
- Attack Vector (Network, Adjacent, Local, Physical)
- Attack Complexity (Low, High)
- Privileges Required (None, Low, High)
- User Interaction (None, Required)
- Scope (Unchanged, Changed)
- Confidentiality Impact (None, Low, High)
- Integrity Impact (None, Low, High)
- Availability Impact (None, Low, High)

### DREAD
- **D**amage: How bad would an attack be?
- **R**eproducibility: How easy to reproduce?
- **E**xploitability: How much work to launch?
- **A**ffected Users: How many impacted?
- **D**iscoverability: How easy to discover?

## Threat Modeling Tools

### Microsoft Threat Modeling Tool
- STRIDE-based analysis
- DFD creation
- Automated threat generation
- Mitigation tracking

### OWASP Threat Dragon
- Open source
- Web-based and desktop
- STRIDE and LINDDUN support

### IriusRisk
- Commercial platform
- Library of threats and controls
- Integration with CI/CD
- Compliance mapping

## Common Threat Scenarios

### Web Application Threats
1. **Injection Attacks**
   - SQL, NoSQL, LDAP injection
   - Command injection
   - XPath injection

2. **Authentication Threats**
   - Brute force attacks
   - Credential stuffing
   - Session fixation

3. **Authorization Threats**
   - Privilege escalation
   - Insecure direct object references
   - Missing function level access control

### API Threats
1. **Rate Limiting Issues**
   - Resource exhaustion
   - Data harvesting
   - Brute force attacks

2. **Data Exposure**
   - Excessive data in responses
   - Sensitive data in URLs
   - Debug information leakage

### Cloud Infrastructure Threats
1. **Misconfiguration**
   - Public S3 buckets
   - Open security groups
   - Default credentials

2. **Identity and Access**
   - Over-privileged roles
   - Credential compromise
   - Lateral movement

## Mitigation Strategies

### Security Controls Mapping
**Preventive Controls:**
- Input validation
- Access controls
- Encryption
- Secure coding

**Detective Controls:**
- Logging and monitoring
- Intrusion detection
- File integrity monitoring
- Anomaly detection

**Corrective Controls:**
- Incident response
- Backup and recovery
- Patch management
- Configuration management

## Threat Modeling Process

### Phase 1: Preparation
1. Define scope and objectives
2. Gather documentation
3. Identify stakeholders
4. Schedule workshops

### Phase 2: Discovery
1. Create architecture diagrams
2. Identify assets and entry points
3. Define trust boundaries
4. Document data flows

### Phase 3: Analysis
1. Apply threat methodology (STRIDE/PASTA)
2. Create attack trees
3. Identify vulnerabilities
4. Score and prioritize risks

### Phase 4: Mitigation
1. Design security controls
2. Create implementation plan
3. Assign ownership
4. Set timelines

### Phase 5: Validation
1. Review mitigation effectiveness
2. Residual risk assessment
3. Acceptance criteria
4. Continuous monitoring plan

## Best Practices

1. **Start Early:** Threat model during design phase
2. **Iterate Regularly:** Update with system changes
3. **Collaborate:** Include developers, architects, security
4. **Document Everything:** Maintain threat model artifacts
5. **Automate Where Possible:** Use tools for consistency
6. **Focus on High-Value Assets:** Prioritize critical data
7. **Consider Insider Threats:** Not just external attackers
8. **Review Regularly:** Annual reviews minimum
9. **Learn from Incidents:** Update based on real attacks
10. **Train the Team:** Build security awareness