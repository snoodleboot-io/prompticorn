# API Security (Minimal)

## Purpose
Identify and close the failure modes specific to APIs — where the caller is a program, every endpoint is directly reachable, and the UI enforces nothing.

## Core Techniques

### 1. Authorize Every Object, Not Just the Route
Broken object-level authorization (BOLA) is the top API vulnerability because route-level checks pass while the object belongs to someone else.

```python
# ❌ Authenticated, but any logged-in user can read any invoice
@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user=Depends(current_user)):
    return db.query(Invoice).get(invoice_id)

# ✅ Ownership is part of the query, not an afterthought
    return db.query(Invoice).filter_by(id=invoice_id, tenant_id=user.tenant_id).one_or_none()
```
Scoping in the `WHERE` clause is stronger than a post-fetch `if`: there is no path where a developer forgets the check and still gets a row. See `authorization-patterns` for the policy models.

### 2. Allowlist Input Fields — Never Bind the Whole Body
```python
# ❌ Mass assignment: attacker POSTs {"email": "...", "role": "admin"}
user.update(**request.json)

# ✅ Explicit schema; unknown keys rejected
class UserPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    display_name: str = Field(max_length=100)
```
`extra="forbid"` matters more than the types: silently ignoring unknown fields hides the attack, rejecting them surfaces it.

### 3. Treat Server-Side Fetches as Hostile (SSRF)
Any endpoint that takes a URL — webhooks, avatar import, PDF render — can be aimed at `169.254.169.254` (cloud metadata) or internal services. Resolve the hostname, reject private/link-local/loopback ranges, re-check after every redirect (DNS can rebind between check and connect), and prefer an egress proxy allowlist over per-call validation.

### 4. Fail Closed, and Fail Quietly
| Situation | Right response |
|---|---|
| Auth service unreachable | 503, deny — never "allow on error" |
| Object exists but not yours | 404, not 403 — 403 confirms existence |
| Unhandled exception | Generic message; stack trace to logs only |

### 5. Version and Retire Endpoints
`/v1/users` left running after `/v2/users` ships keeps the old, weaker validation alive. Shadow and zombie endpoints are exploited precisely because nobody is looking at them. Generate the inventory from the router table, not from the docs.

### 6. Rate-Limit by Identity, Not Just IP
An authenticated API's expensive endpoints (search, export, report generation) need per-principal quotas. IP limits are trivially bypassed by any distributed client and punish shared NATs. Concrete limiter configuration lives in `api-security-hardening`.

## Warning Signs

- Handlers that fetch by id and then check ownership, or don't check at all
- Request models built by spreading the JSON body into an ORM object
- Sequential integer ids exposed in URLs with no tenant scoping in the query
- 403 for other users' resources (existence oracle) and 404 for your own
- Any endpoint accepting a caller-supplied URL or hostname
- Error responses containing SQL, stack frames, or internal hostnames
- Endpoints in production that appear in no API spec or test suite
- Rate limits applied at the edge only, keyed solely on client IP
