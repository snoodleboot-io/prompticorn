# Authorization Patterns (Verbose)

## Core Patterns

### Role-Based Access Control

RBAC assigns permissions to roles and roles to subjects. The discipline that
keeps it maintainable is that application code asks about *permissions*, never
about role names.

```python
ROLE_PERMISSIONS = {
    "viewer":  {"document:read"},
    "editor":  {"document:read", "document:write"},
    "owner":   {"document:read", "document:write", "document:delete", "document:share"},
    "billing": {"invoice:read", "invoice:refund"},
}

def permissions_of(principal) -> frozenset[str]:
    return frozenset().union(*(ROLE_PERMISSIONS[r] for r in principal.roles))
```

Role names in `if` statements are the failure mode: adding `billing_admin` then
requires editing every handler that special-cased `admin`. Permissions are a
stable interface; roles are a convenience for humans assigning them.

RBAC's real limit is that it is per-*type*, not per-*instance*. "Editor" says a
user may edit documents — not which ones. Instance-level control needs either a
scope carried alongside the role (`editor@org:42`) or a different model.

### Attribute-Based Access Control

ABAC evaluates a rule over attributes of the subject, resource, action, and
environment. It expresses conditions RBAC cannot.

```rego
package authz

default allow = false

allow {
    input.action == "record:read"
    input.subject.department == input.resource.department
    input.subject.clearance >= input.resource.classification
}
```

The trade-off is directional. Answering "may Alice read record 7?" is cheap.
Answering "which records may Alice read?" requires evaluating the policy against
every record, or reimplementing it as a database predicate — and those two
implementations drift. Design the list endpoint's filter and the point check
from the same source of truth, or accept that they will disagree.

Cedar expresses the same shape as `permit (principal, action ==
Action::"record:read", resource) when { principal.clearance >=
resource.classification };`.

### Relationship-Based Access Control

ReBAC (the Zanzibar model, implemented by SpiceDB and OpenFGA) stores
relationships as tuples and answers questions by traversing the graph.

```
document:readme#owner@user:alice
folder:eng#viewer@group:engineering#member
document:readme#parent@folder:eng
```

with a schema saying `viewer` on a document is inherited from `viewer` on its
parent folder. Alice's team lead gets access by being in `group:engineering`,
with no per-document tuple written.

| Question | RBAC | ABAC | ReBAC |
|---|---|---|---|
| Can Alice edit doc 7? | Cheap | Cheap | Cheap (graph check) |
| List everything Alice can edit | Cheap | Expensive | Cheap (reverse expand) |
| Who can edit doc 7? | Cheap | Very expensive | Cheap (expand) |
| Rule uses time of day / IP | No | Yes | Not natively |
| Nested sharing, folders, groups | Painful | Painful | Native |

ReBAC's cost is a new consistency problem: the tuple store is separate from your
database. Zanzibar-style systems expose consistency tokens (a "zookie") so a
check can be required to observe a just-written tuple; skipping that gives you a
new-share-not-visible bug, and demanding full consistency everywhere gives up
the caching that makes the system fast.

### Where Enforcement Lives

| Layer | Sees | Good for | Cannot do |
|---|---|---|---|
| Gateway / mesh | Route, JWT claims | Coarse deny, tenant routing | Object-level decisions |
| Service handler | Principal + loaded object | Business rules | Guarantee no path skips it |
| Data access layer | Every query | Systematic tenant scoping | Cross-service rules |
| Database (RLS) | All SQL, all clients | The backstop | Application-level context |

Defense in depth means the gateway rejects the obviously unauthorized, the
service makes the real decision, and the data layer refuses to return
out-of-scope rows even when the service forgets. Postgres RLS is the strongest
of these because scripts, migrations, and report queries inherit it:

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON documents
  USING      (org_id = current_setting('app.org_id')::uuid)   -- reads/updates
  WITH CHECK (org_id = current_setting('app.org_id')::uuid);  -- writes
```

`USING` without `WITH CHECK` is a common half-implementation: a tenant can then
insert or update a row *into* another tenant. Also note the table owner and
superusers bypass RLS unless you set `FORCE ROW LEVEL SECURITY`, so the
application must not connect as the owning role.

### Making Bypass Impossible

The durable fix is structural: make the unauthorized call fail to compile or
fail loudly, rather than relying on reviewers noticing an omission.

```python
@router.get("/documents/{doc_id}")
@requires("document:read", resource=load_document)   # decorator resolves and checks
def read(doc: Document):
    return DocumentOut.model_validate(doc)
```

Pair that with a test that enumerates the router and asserts every route is
either decorated or on an explicit public allowlist — new endpoints then fail CI
instead of shipping open.

### Deciding Under Failure and Delegation

Fail closed. If the PDP times out, deny and return 503; "allow on error" turns a
policy-service outage into a full authorization bypass. Cache decisions with a
short TTL (seconds) and a revocation channel, and remember that caching a
*decision* is safer than caching a *role set*, because the decision key includes
the resource.

For impersonation, carry both identities: an audit line reading "admin@corp
acting as user:9182 deleted invoice 55" is recoverable; "user:9182 deleted
invoice 55" is not.

## Common Anti-Patterns

❌ **Checking role names in handlers** — every new role touches every file.
✅ Handlers check permissions; roles map to permissions in one place.

❌ **Authorization in the frontend** — hidden buttons stop nobody with curl.
✅ The server decides; the UI merely reflects the decision.

❌ **Fetch then filter** — other tenants' rows are already in memory, logs, and
error reports.
✅ Scope the query; enforce with RLS as a backstop.

❌ **Permissions embedded in a long-lived JWT** — revoking a role has no effect
until expiry, sometimes days.
✅ Short-lived tokens, or resolve permissions server-side per request.

❌ **Allow-overrides-deny, or ignoring policy errors.**
✅ Default deny; deny wins; an evaluation error is a denial.

❌ **A wildcard `admin` role that bypasses all checks** — it becomes the account
every integration uses, and the blast radius of one leaked key.
✅ Scope even administrative power by resource and action, and audit its use.

❌ **Reimplementing the policy in the list endpoint's SQL** — the point check and
the filter drift apart within a quarter.
✅ Generate the filter from the policy, or centralize both behind one API.

## Authorization Checklist

- [ ] The access model (RBAC / ABAC / ReBAC) is a deliberate, documented choice
- [ ] Handlers check permissions or policy decisions, never role name strings
- [ ] One decision function; no ad-hoc checks embedded in business logic
- [ ] Default deny, with deny taking precedence over allow
- [ ] PDP unavailability results in denial, not a fallback allow
- [ ] Every query carries a tenant/owner predicate; RLS enabled as a backstop
- [ ] RLS policies define both `USING` and `WITH CHECK`; app role is not the owner
- [ ] Object-level checks exist on bulk, export, and admin endpoints
- [ ] A CI test asserts every route is guarded or explicitly public
- [ ] Negative tests cover cross-tenant and cross-user access for each resource
- [ ] Permission changes take effect within a bounded, known interval
- [ ] Impersonation records both the acting and the effective principal
- [ ] Authorization denials are logged with principal, action, and resource
- [ ] Role and permission assignments are reviewed on a schedule
