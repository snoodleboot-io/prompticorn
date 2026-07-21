# Security Architecture Review (Verbose)

## Core Patterns

### Establishing the Model

You cannot review what you cannot see. Before any judgment, produce four artifacts:

1. **Component diagram** — processes, datastores, queues, external services
2. **Data flow** — what moves between them, in what direction, carrying what
3. **Trust boundaries** — every crossing between differing privilege levels
4. **Asset inventory** — what is actually worth stealing, and where it rests

```
                    ╔═══ trust boundary: public → edge ═══╗
[Browser] ──TLS 1.3──> [CDN + WAF] ──> [API Gateway: authn, rate limit]
                    ╚══════════════════════════╤══════════╝
                                               │ signed JWT (aud, exp 5m)
                    ╔═══ trust boundary: edge → service mesh ═══╗
                    ║  [Order Svc] ──mTLS──> [Inventory Svc]    ║
                    ║       │                                    ║
                    ║       ├── role: order_rw ──> [Postgres: orders schema]
                    ║       └── publishes ──────> [Kafka: order.events]
                    ╚════════════════════╤═══════════════════════╝
                                         │ boundary: third party
                              [Payment Provider API]
```

Asset inventory drives severity. A design flaw exposing session tokens and one
exposing feature-flag names are not the same finding, and treating them alike is
how architecture reviews lose credibility with the teams they serve.

### Threat Modeling: STRIDE Applied per Boundary

Walk each boundary, not each component. The interesting failures are at crossings.

| Boundary | Spoofing | Tampering | Info disclosure | Elevation |
|---|---|---|---|---|
| Browser → edge | Stolen session | Request replay | TLS downgrade | Forged role claim |
| Edge → service | Direct-to-origin bypass | Header injection | Verbose errors | Unverified `X-User-Id` |
| Service → service | Any pod can call | Unsigned messages | Over-broad response | Missing audience check |
| Service → DB | Shared credential | No integrity check | `SELECT *` cross-tenant | DDL rights in prod |
| System → third party | No mTLS or key pinning | Unsigned webhook | PII in payload | Callback trusted blindly |

For each cell, record the control, or record the accepted risk with an owner. A
threat model whose output is prose nobody can act on is theater; the output should
be a list of controls and a list of explicitly accepted gaps.

### Authorization Architecture

Where authorization is *decided* and where it is *enforced* are different design
choices, and conflating them is the most common architectural defect.

| Model | Decision point | Trade-off |
|---|---|---|
| Edge-only | Gateway | Simple; one bypass defeats everything |
| Per-service | Each service | Robust; policy duplication and drift |
| Central PDP (OPA-style) | Policy service, cached | Consistent policy; PDP is a dependency and a target |
| Data-layer (RLS) | Database | Cannot be forgotten by a handler; harder to reason about |

Defense in depth means the resource itself re-checks:

```sql
-- Postgres row-level security: tenancy enforced below the application,
-- so a handler that forgets its WHERE clause still cannot cross tenants
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
  USING (org_id = current_setting('app.current_org')::uuid);
```

This is the structural fix for the class of bug that
`secure-code-review` catches one instance at a time.

### Service Identity and Least Privilege

```yaml
# ❌ one credential, unlimited reach — compromise of any service is total
DATABASE_URL: postgres://app_user:hunter2@db/prod   # superuser, all schemas

# ✅ per-service identity, scoped grants, short-lived credentials
# IAM auth token, 15-minute lifetime, issued to this workload identity only
DATABASE_HOST: db.internal
DATABASE_USER: svc_orders          # GRANT SELECT,INSERT,UPDATE ON orders TO svc_orders;
DATABASE_AUTH: iam                 # no static password anywhere
```

The review question is not "is the credential strong" but "what does holding it
buy". Rate the blast radius per component and treat anything with system-wide
reach as a design finding, not a hardening suggestion.

### Data Protection by Classification

| Class | Examples | At rest | In transit | Retention |
|---|---|---|---|---|
| Public | Docs, marketing | None required | TLS | Indefinite |
| Internal | Logs, metrics | Volume encryption | TLS | 30–90 days |
| Confidential | PII, customer content | Envelope encryption, KMS | TLS 1.2+ | Per contract |
| Restricted | Card data, health, credentials | Field-level + separate key | mTLS | Minimum lawful |

Field-level encryption on restricted data means a database dump is not a breach
of that field — but only if the key lives outside the database and the decrypt
call is audited. Encryption whose key sits beside the ciphertext is a compliance
checkbox, not a control.

### Failure Modes and Degradation

Ask what the system does when each dependency fails. The dangerous answer is
"continues serving".

- Authz service unreachable → deny, do not cache-and-allow indefinitely
- Token signature key fetch fails → reject tokens, do not skip verification
- WAF bypassed via direct-to-origin → origin must require the edge's mTLS identity
- Rate limiter's Redis down → fall back to a conservative local limit, not unlimited
- Audit log write fails → for restricted operations, fail the operation

## Common Anti-Patterns

❌ **Perimeter-only security** — hard shell, flat interior; one SSRF or one
compromised pod yields the whole estate.
✅ Authenticate and authorize at every hop; assume the interior is hostile.

❌ **Trusting internal headers** — `X-User-Id`, `X-Role`, `X-Forwarded-For` set by
the gateway and consumed downstream with no integrity protection.
✅ Signed, audience-scoped, short-lived tokens verified by the callee.

❌ **Shared database credential across all services** — the blast radius of any
single compromise becomes total.
✅ Per-service identity with schema- and operation-scoped grants.

❌ **Tenancy enforced only in application code** — one forgotten `WHERE` leaks
across customers, and there is no second line of defense.
✅ Row-level security or a per-tenant schema beneath the application.

❌ **Secrets with no rotation story** — a static key in a config map is a
permanent, undetectable compromise once leaked.
✅ Vault or cloud KMS, short TTLs, automated rotation, revocation you have tested.

❌ **Security controls only in the client or the WAF** — both are bypassable by
definition; a WAF rule is compensating, never primary.
✅ Enforce server-side; treat edge controls as latency and noise reduction.

❌ **Reviewing the design once at kickoff** — the built system diverges within weeks.
✅ Re-review on any change to a trust boundary, authn/authz model, data
classification, or third-party integration.

❌ **Findings without severity or an owner** — the report is filed and nothing changes.
✅ Every finding gets a rated blast radius, a named owner, and a decision:
fix, compensate, or accept with an expiry date.

## Architecture Review Checklist

- [ ] Current component and data-flow diagram exists and matches reality
- [ ] Every trust boundary explicitly marked, with a control at each crossing
- [ ] STRIDE walked per boundary; results are actionable controls, not prose
- [ ] Assets classified; protection matches classification
- [ ] Authentication method defined for every caller, including service-to-service
- [ ] Authorization enforced at the resource, not only at the edge
- [ ] Multi-tenant isolation enforced below the application (RLS or schema)
- [ ] Per-service credentials, least-privilege grants, short-lived where possible
- [ ] Blast radius rated per component; no component holds system-wide reach
- [ ] Secrets management with defined rotation and a tested revocation path
- [ ] Encryption keys held outside the data they protect; decrypt calls audited
- [ ] All dependency failures degrade closed
- [ ] Origin rejects requests that did not transit the edge
- [ ] Third-party integrations scoped, timed out, and signature-verified
- [ ] Audit logs append-only and not writable by the audited service
- [ ] Each finding carries severity, owner, and fix/compensate/accept decision
