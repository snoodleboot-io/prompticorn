# Security Architecture Review (Minimal)

## Purpose
Evaluate a system's design — its trust boundaries, data flows, and blast radius —
to find flaws that no amount of correct code at the line level can fix.

## Core Techniques

### 1. Draw the Trust Boundaries First
A trust boundary is any place data or control crosses between principals with
different privilege. Every boundary needs an answer to: who is calling, what may
they do, and what happens if the caller is lying?

```
[Browser] ──TLS──> [CDN/WAF] ──> [API Gateway] ══> [Order Service] ──> [Postgres]
    ↑ untrusted          ↑ boundary: authn      ↑ boundary: authz   ↑ boundary: data
                                                       │
                                                       └──> [Payment Provider]  ← boundary: third party
```
The bug is usually at a boundary someone forgot to draw — an internal service
that trusts a header, or a queue any pod can publish to.

### 2. Threat Model with STRIDE per Boundary
| Threat | Question | Typical control |
|---|---|---|
| **S**poofing | Can I claim to be someone else? | Strong authn, mTLS |
| **T**ampering | Can I alter data in flight or at rest? | TLS, signatures, integrity checks |
| **R**epudiation | Can an action be denied later? | Tamper-evident audit log |
| **I**nformation disclosure | Can I read what I shouldn't? | Encryption, authz, field-level scoping |
| **D**enial of service | Can I exhaust it? | Quotas, rate limits, timeouts |
| **E**levation of privilege | Can I gain rights? | Least privilege, boundary re-checks |

### 3. Re-Authorize at Every Hop
```yaml
# ❌ Gateway authenticates, then services trust an unsigned header
X-User-Id: 4711          # any pod on the network can forge this

# ✅ Propagate a signed, audience-scoped token the callee verifies itself
Authorization: Bearer <JWT aud=order-service, exp=+5m, sub=4711>
```
"The network is internal" is not an authorization decision. Assume an attacker
already has a foothold inside it and design so that buys them little.

### 4. Size the Blast Radius
For each component ask: if this is fully compromised, what does the attacker
reach? A service with a database credential that can `SELECT *` across all
tenants is a single-point catastrophic failure regardless of code quality.
Scope credentials per-service, per-table, and per-operation; prefer short-lived
issued credentials over long-lived static ones.

### 5. Locate the Secrets and the Keys
Trace where every secret is created, stored, distributed, rotated, and revoked.
A design with no rotation story has a permanent compromise story. Note which
keys protect data at rest, who can call the decrypt operation, and whether the
audit log would show them doing it.

### 6. Check the Failure and Degradation Modes
What happens when the authz service is down, the token cache is cold, or the WAF
is bypassed by a direct-to-origin request? Designs that degrade *open* under load
are the ones that fail during an incident, which is exactly when they are attacked.

## Warning Signs

- No diagram, or a diagram with no boundary markings
- Internal services that trust headers, IP ranges, or "it's in the VPC"
- One database credential shared by every service, with full DDL rights
- Authorization performed only at the edge, never re-checked at the resource
- Multi-tenant data with no tenant id in the primary key or row-level policy
- Secrets with no defined rotation or revocation path
- Third-party integrations with no scoping, no timeout, and no failure behavior
- Audit logs writable by the service they audit
- Security controls that live only in the client or the WAF
