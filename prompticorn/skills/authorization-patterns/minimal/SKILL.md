# Authorization Patterns (Minimal)

## Purpose
Choose an access-control model — RBAC, ABAC, or ReBAC — and enforce it in one place that no code path can route around.

## Core Techniques

### 1. Pick the Model That Matches the Question
| Model | Decides on | Fits | Breaks down when |
|---|---|---|---|
| RBAC | Role held by the subject | Small fixed job functions | Roles multiply per-customer ("editor_eu_readonly") |
| ABAC | Attributes of subject, resource, environment | Conditional rules (clearance, region, time) | "Who can see X?" needs evaluating every rule |
| ReBAC | Graph edges between subject and object | Sharing, nesting, ownership (docs, repos, folders) | Rules depend on non-relational attributes |

Most systems end up RBAC for coarse capability plus per-object ownership checks. Adopt a policy engine when the rules outgrow `if user.role == ...`, not before.

### 2. Separate the Decision From the Enforcement
The policy decision point (PDP) answers *may this principal do this?*; the policy enforcement point (PEP) is the single call site that asks. One PDP, many PEPs.

```python
# ✅ Every handler goes through one function; the rules live in one module
def authorize(principal, action: str, resource) -> None:
    if not policy.allows(principal, action, resource):
        raise Forbidden()

authorize(user, "document:publish", doc)
```
Scattering `if role == "admin"` across 40 handlers means no one can answer "who can publish?" without grepping.

### 3. Enforce on the Server, at the Data Boundary
Hiding a button is UX, not authorization. Filtering after fetch still loads other tenants' rows into memory and into logs. Push the constraint into the query:

```python
q = session.query(Document).filter(Document.org_id == principal.org_id)
```

### 4. Default Deny, and Deny Wins
Unknown action, unknown resource type, or an error evaluating policy must all return deny. When both an allow and a deny rule match, deny takes precedence — otherwise adding a permission can silently revoke a restriction.

### 5. Check Permissions, Not Roles
```python
# ❌ Every new role edits every handler
if user.role in ("admin", "owner", "billing_admin"): ...

# ✅ Roles map to permissions; handlers ask about permissions
if "invoice:refund" in principal.permissions: ...
```

### 6. Re-Evaluate on Every Request
Permissions baked into a long-lived JWT are stale from the moment they are signed — revoking a role does nothing until expiry. Keep the token short-lived, or resolve permissions server-side per request and cache with a short TTL you can invalidate.

## Warning Signs

- Ownership checked in some handlers and forgotten in others
- Authorization implemented in the frontend, or by omitting a route from the nav
- `role == "admin"` string comparisons scattered through business logic
- Roles created per customer, or a `permissions` list edited by hand in prod
- Any code path reaching the ORM without a tenant/org predicate
- Policy failures that fall through to allow (`try/except: pass` around a check)
- Bulk, export, and admin endpoints with only route-level auth
- No test asserting that user A cannot read user B's object
