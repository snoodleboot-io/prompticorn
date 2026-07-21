# Threat Modeling (Minimal)

## Purpose
A structured pass over a design — diagram, trust boundaries, STRIDE, mitigations — that finds whole classes of flaws while they are still cheap to fix.

## Core Techniques

### 1. Answer the Four Questions
Threat modeling is Shostack's four questions, in order. Everything else is technique for answering them.

```
1. What are we building?        -> data flow diagram with trust boundaries
2. What can go wrong?           -> STRIDE per element
3. What are we going to do?     -> mitigate / transfer / accept / eliminate
4. Did we do a good job?        -> tracked issues, verified in test
```

### 2. Draw a Data Flow Diagram, Not an Architecture Diagram
A DFD has four shapes and one thing an architecture diagram lacks: boundaries.

```
[External entity]  ( Process )  || Data store ||  --> data flow  ==== trust boundary
```

```
  Browser                              ==== internet / DMZ boundary
     |  1. POST /api/v1/expenses (JWT)
     v
  ( API service ) ------------------- ==== app / data boundary
     |  2. SQL           \  3. PutObject
     v                    v
  || Postgres ||        || S3 receipts ||
     |
     |  4. HTTPS receipt image        ==== org boundary (vendor)
     v
  ( OCR vendor )
```

Every arrow crossing a `====` is where privilege, trust, or ownership changes — and that is where the threats are. Flow 4 leaves your organization entirely: the vendor now holds receipt images containing PII.

### 3. Run STRIDE Per Element
Walk each element and ask the six questions. Applied to the API service above:

| STRIDE | Threat on the API service | Mitigation |
|---|---|---|
| **S**poofing | Forged JWT via `alg: none` | Pin `algorithms=["RS256"]`, verify `aud`/`iss` |
| **T**ampering | Client sends `amount` and `approved: true` | Server-side authoritative fields; ignore client state |
| **R**epudiation | Approver denies approving | Append-only audit log, shipped off-host |
| **I**nfo disclosure | IDOR on `GET /expenses/:id` | Tenant-scope every query, not just the route |
| **D**oS | 10k PDF renders queued | Per-tenant rate limit, bounded worker pool |
| **E**levation | Renderer SSRF → instance metadata | Egress allowlist, IMDSv2, no pod credentials |

STRIDE does not apply uniformly: external entities can only be spoofed or repudiate; data stores cannot spoof. Use the per-element mapping rather than forcing six threats onto everything.

### 4. Map Every Threat to a Decision
A threat model that ends in a list of threats has not finished. Each one gets one of four dispositions.

| Disposition | Meaning | Example |
|---|---|---|
| Eliminate | Remove the feature or the asset | Stop storing full card numbers |
| Mitigate | Add a control | Tenant-scoped queries for the IDOR |
| Transfer | Someone else carries it | Vendor's PCI scope, contractual DPA |
| Accept | Documented, owned, dated | Vendor breach risk, reviewed quarterly |

"Accept" is legitimate — silently ignoring is not. Write down who accepted it and when it gets revisited.

### 5. Model at Design Time, Not Ship Time
A pentest tells you the deployed system has an IDOR on one endpoint. A threat model tells you no endpoint enforces tenant scoping, which is an architecture defect and probably affects all 43 routes. The pentest finds instances; the model finds the class. It also arrives before the design is expensive to change — a missing trust boundary is a whiteboard edit in week one and a migration in month nine. Do both: model at design, pentest to verify.

## Warning Signs

- Diagrams with no trust boundaries drawn on them
- Third-party services and CI missing from the diagram entirely
- STRIDE applied only to the "important" component, never to data stores or flows
- Threats identified but never assigned a disposition or an owner
- Accepted risks with no name and no review date
- The model was built once, before the design changed twice
- Every threat mitigated by "input validation" — which addresses tampering, not authorization
- No linkage from a modeled threat to a test that would catch its regression
