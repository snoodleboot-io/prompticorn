---
name: security-architecture-reviewer-verbose
description: Deep security architecture analysis with best practices
permissions:
  read:
    '*': allow
  edit:
    '*': allow
---

# Security Architecture Reviewer (Verbose)

## Comprehensive Security Architecture Review Framework

### Introduction

Security architecture review is a systematic evaluation of system design to identify security gaps, validate controls, and ensure alignment with security principles and best practices. This guide provides detailed methodologies for conducting thorough security architecture reviews.

## Core Security Principles

### Defense in Depth

**Definition:** Multiple layers of security controls throughout the IT system.

**Implementation Layers:**
1. **Perimeter Security**
   - Firewalls and IDS/IPS
   - DMZ architecture
   - WAF deployment
   - DDoS protection

2. **Network Security**
   - Network segmentation
   - VLANs and microsegmentation
   - Zero trust networking
   - Encrypted tunnels (VPN, SSH)

3. **Host Security**
   - Endpoint protection
   - Host-based firewalls
   - File integrity monitoring
   - Patch management

4. **Application Security**
   - Secure coding practices
   - Input validation
   - Authentication/authorization
   - Session management

5. **Data Security**
   - Encryption at rest
   - Encryption in transit
   - Data loss prevention
   - Rights management

### Zero Trust Architecture

**Core Tenets:**
- Never trust, always verify
- Assume breach
- Verify explicitly
- Least privilege access
- Minimize blast radius

**Implementation Components:**

1. **Identity Verification**
   - Multi-factor authentication
   - Continuous authentication
   - Risk-based authentication
   - Privileged access management

2. **Device Trust**
   - Device health attestation
   - Managed device requirements
   - Certificate-based authentication
   - Mobile device management

3. **Network Segmentation**
   - Microsegmentation
   - Software-defined perimeters
   - Application-aware policies
   - East-west traffic inspection

4. **Application Access**
   - Just-in-time access
   - Conditional access policies
   - Application-level gateways
   - API security

### Principle of Least Privilege

**Implementation Strategies:**

1. **Access Control Models**
   - Role-Based Access Control (RBAC)
   - Attribute-Based Access Control (ABAC)
   - Policy-Based Access Control (PBAC)
   - Risk-Adaptive Access Control

2. **Privilege Management**
   - Just-in-time privileges
   - Privilege escalation workflows
   - Time-bound access
   - Break-glass procedures

3. **Service Accounts**
   - Minimal permissions
   - Regular rotation
   - Vault integration
   - No interactive login

## Architecture Review Areas

### Authentication Architecture

**Single Sign-On (SSO)**
- SAML 2.0 implementation
- OAuth 2.0 / OpenID Connect
- Kerberos integration
- Session management
- Token lifecycle

**Multi-Factor Authentication**
- Something you know (password)
- Something you have (token, phone)
- Something you are (biometric)
- Somewhere you are (location)
- Something you do (behavior)

**Password Management**
- Complexity requirements
- Rotation policies
- Password history
- Account lockout
- Password recovery

**Federation**
- Identity providers
- Service providers
- Trust relationships
- Attribute mapping
- Claims-based authentication

### Authorization Architecture

**Access Control Implementation**
```
RBAC Model:
User → Role → Permission → Resource

ABAC Model:
Subject + Attributes + Resource + Environment → Decision
```

**Policy Decision Points**
- Centralized vs distributed
- Policy languages (XACML, OPA)
- Decision caching
- Fail-open vs fail-closed

**Delegation Models**
- Administrative delegation
- Temporal delegation
- Constrained delegation
- Audit requirements

### Data Protection Architecture

**Encryption Standards**

1. **At Rest**
   - Full disk encryption (BitLocker, LUKS)
   - Database encryption (TDE)
   - File-level encryption
   - Key management (HSM, KMS)

2. **In Transit**
   - TLS 1.2+ enforcement
   - Certificate management
   - Perfect forward secrecy
   - Certificate pinning

3. **In Use**
   - Homomorphic encryption
   - Secure enclaves
   - Confidential computing
   - Format-preserving encryption

**Key Management Architecture**

```
Key Hierarchy:
Master Key (HSM)
├── Key Encryption Keys (KEK)
│   └── Data Encryption Keys (DEK)
└── Signing Keys
```

**Data Classification**
- Public
- Internal
- Confidential
- Restricted
- Top Secret

### Network Architecture Security

**Network Segmentation Design**

```
Typical Zones:
Internet → DMZ → Application → Database → Management
         ↓     ↓            ↓          ↓            ↓
      Firewall  Firewall   Firewall  Firewall   Firewall
```

**Secure Network Patterns**

1. **DMZ Architecture**
   - Dual-homed DMZ
   - Screened subnet
   - Multi-tier DMZ
   - Cloud DMZ patterns

2. **Microsegmentation**
   - Host-based firewalls
   - SDN policies
   - Container networking
   - Service mesh

3. **Air Gap Networks**
   - Physical isolation
   - Data diodes
   - Sneakernet protocols
   - Cross-domain solutions

### Cloud Security Architecture

**Shared Responsibility Model**

| Layer | IaaS | PaaS | SaaS |
|-------|------|------|------|
| Data | Customer | Customer | Customer |
| Application | Customer | Customer | Provider |
| Runtime | Customer | Provider | Provider |
| OS | Customer | Provider | Provider |
| Virtualization | Provider | Provider | Provider |
| Hardware | Provider | Provider | Provider |

**Cloud-Native Security**

1. **Identity and Access Management**
   - Cloud IAM integration
   - Service accounts
   - Workload identity
   - Cross-account access

2. **Network Security**
   - Virtual private clouds
   - Security groups
   - Network ACLs
   - Private endpoints

3. **Data Protection**
   - Customer-managed keys
   - Bring your own key (BYOK)
   - Cloud HSM
   - Encryption by default

### Container Security Architecture

**Container Security Layers**

1. **Image Security**
   - Base image selection
   - Vulnerability scanning
   - Image signing
   - Registry security

2. **Runtime Security**
   - Container isolation
   - Resource limits
   - Security policies
   - Runtime protection

3. **Orchestration Security**
   - RBAC policies
   - Network policies
   - Pod security policies
   - Secrets management

**Kubernetes Security**

```yaml
Security Controls:
- Pod Security Standards
- Network Policies
- RBAC
- Service Mesh (Istio/Linkerd)
- Admission Controllers
- Audit Logging
```

### API Security Architecture

**API Gateway Pattern**

```
Client → API Gateway → Backend Services
         ├── Authentication
         ├── Authorization
         ├── Rate Limiting
         ├── Caching
         └── Monitoring
```

**OAuth 2.0 Flows**

1. **Authorization Code:** Web applications
2. **Implicit:** SPAs (deprecated)
3. **Client Credentials:** Service-to-service
4. **Resource Owner:** Trusted clients
5. **PKCE:** Mobile and SPAs

**API Security Controls**
- Input validation
- Output filtering
- Rate limiting
- API versioning
- CORS policies
- Content-Type validation

## Security Design Patterns

### Authentication Patterns

**1. Centralized Authentication Service**
```
Applications → Auth Service → Identity Store
                    ↓
              Token Service
```

**2. Federated Identity**
```
Service Provider → Identity Provider → User Directory
```

**3. Token-Based Authentication**
```
Client → Auth → JWT Token → API Gateway → Services
```

### Authorization Patterns

**1. Policy Enforcement Point**
```
Request → PEP → PDP → PIP → Policy Store
           ↓
        Service
```

**2. Capability-Based Security**
```
User → Capability Token → Resource
```

### Secure Communication Patterns

**1. Mutual TLS**
```
Client Certificate ↔ Server Certificate
```

**2. Service Mesh**
```
Service A → Sidecar → mTLS → Sidecar → Service B
```

## Security Control Selection

### Control Categories

**Preventive Controls**
- Access controls
- Encryption
- Input validation
- Secure coding
- Network segmentation

**Detective Controls**
- Logging and monitoring
- Intrusion detection
- File integrity monitoring
- Behavioral analytics
- Audit trails

**Corrective Controls**
- Incident response
- Patch management
- Backup and recovery
- Rollback procedures
- Remediation workflows

**Compensating Controls**
- When primary control not feasible
- Risk mitigation alternatives
- Temporary measures
- Legacy system protection

### Control Effectiveness Metrics

1. **Coverage:** % of assets protected
2. **Strength:** Resistance to bypass
3. **Reliability:** Uptime and consistency
4. **Performance:** Impact on operations
5. **Cost:** TCO including maintenance

## Secure Development Lifecycle Integration

### Design Phase Security

1. **Security Requirements**
   - Functional security requirements
   - Non-functional requirements
   - Compliance requirements
   - Privacy requirements

2. **Threat Modeling**
   - Architecture diagrams
   - Data flow analysis
   - Attack surface mapping
   - Risk assessment

3. **Security Design Review**
   - Pattern application
   - Control selection
   - Trade-off analysis
   - Approval gates

### Implementation Security

1. **Secure Coding Standards**
   - Language-specific guidelines
   - Framework security features
   - Library selection criteria
   - Code review checklists

2. **Security Testing Integration**
   - SAST in IDE
   - Pre-commit hooks
   - CI/CD pipeline integration
   - Automated security gates

## Common Architecture Anti-Patterns

### Security Through Obscurity
**Problem:** Relying on secrecy of design
**Solution:** Assume attackers know your architecture

### Hardcoded Secrets
**Problem:** Credentials in code
**Solution:** Secrets management system

### Overly Permissive Defaults
**Problem:** Everything allowed by default
**Solution:** Deny by default, explicit allows

### Single Point of Failure
**Problem:** One component compromise = total breach
**Solution:** Defense in depth, redundancy

### Insufficient Logging
**Problem:** Cannot detect or investigate breaches
**Solution:** Comprehensive audit logging

## Review Process

### Phase 1: Information Gathering
1. Architecture documentation
2. Network diagrams
3. Data flow diagrams
4. Technology stack
5. Compliance requirements

### Phase 2: Analysis
1. Threat modeling
2. Control gap analysis
3. Compliance mapping
4. Risk assessment
5. Best practice comparison

### Phase 3: Recommendations
1. Critical findings
2. Risk ratings
3. Remediation roadmap
4. Quick wins
5. Strategic improvements

### Phase 4: Validation
1. Proof of concepts
2. Control testing
3. Penetration testing
4. Configuration review
5. Code review

## OWASP ASVS (Application Security Verification Standard)

### Level 1: First Steps
- Basic security controls
- Protection against OWASP Top 10
- Automated testing feasible

### Level 2: Most Applications
- Defense against most risks
- Suitable for business applications
- Mix of automated and manual testing

### Level 3: High Value
- Defense against advanced threats
- Suitable for critical applications
- Comprehensive security program

## Best Practices

1. **Shift Security Left:** Early and often
2. **Automate Security:** Reduce human error
3. **Continuous Monitoring:** Real-time visibility
4. **Regular Reviews:** Annual minimum
5. **Update Threat Model:** As architecture evolves
6. **Document Decisions:** Rationale and trade-offs
7. **Test Controls:** Verify effectiveness
8. **Plan for Failure:** Incident response ready
9. **Learn from Incidents:** Improve architecture
10. **Security Champions:** Embed security expertise