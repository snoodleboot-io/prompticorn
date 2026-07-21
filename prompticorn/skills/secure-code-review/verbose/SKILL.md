# Secure Code Review (Verbose)

## Core Patterns

### Taint Tracking by Hand

Every review starts the same way: enumerate the sources of attacker-controlled
data, enumerate the dangerous sinks, and ask whether anything sanitizing sits
between them.

| Source | Often forgotten |
|---|---|
| Query string, body, path params | — |
| Headers | `Host`, `X-Forwarded-For`, `Referer`, `User-Agent` |
| Cookies | Values are as attacker-controlled as a form field |
| Uploaded file names and contents | Name drives path traversal; content drives parser bugs |
| Webhook payloads | Signed? Verified *before* parsing? |
| Database rows | Tainted if a user wrote them — stored XSS lives here |

| Sink | Safe construction |
|---|---|
| SQL | Bound parameters |
| Shell | `subprocess.run([...])`, no `shell=True` |
| HTML | Contextual auto-escaping template engine |
| File path | Resolve, then assert the prefix is inside the base dir |
| Outbound HTTP | Allowlist of hosts, resolve-then-check the IP |
| Deserializer | JSON only; never `pickle`, `yaml.load`, or Java native |

The database row is the one people miss. Data validated on the way in is still
attacker-authored on the way out, and a template rendering it with `|safe`
reintroduces XSS from storage.

### Injection: The Shapes That Recur

```python
# ❌ concatenation — the value is parsed as SQL syntax
cur.execute("SELECT * FROM orders WHERE status = '" + status + "'")

# ✅ bound parameter — query and data travel separately
cur.execute("SELECT * FROM orders WHERE status = %s", (status,))
```

Identifiers cannot be bound. When a column or table name is dynamic, validate it
against a hardcoded allowlist — never quote-and-hope:

```python
SORTABLE = {"created_at", "total", "status"}
if sort not in SORTABLE:
    raise ValueError(sort)
cur.execute(f"SELECT * FROM orders ORDER BY {sort}")   # safe: value came from the set
```

```python
# ❌ shell metacharacters become code
os.system(f"convert {filename} out.png")
# ✅ argv list, no shell involved
subprocess.run(["convert", filename, "out.png"], check=True)
```

```python
# ❌ path traversal via "../../etc/passwd"
open(os.path.join(BASE, user_path))
# ✅ resolve, then confine
full = (BASE / user_path).resolve()
if not full.is_relative_to(BASE.resolve()):
    raise PermissionError
```

### Authorization Review

Read every handler against three questions. They fail independently.

1. **Authenticated?** Is there a session or token, validated *here* rather than
   assumed from an upstream proxy that may be bypassable?
2. **Entitled?** Does this role have this function at all?
3. **Object-level?** Does *this* principal own *this* record?

Broken object-level authorization is the highest-yield finding a human reviewer
produces, precisely because the code looks correct — the bug is a missing clause,
and no linter has the domain knowledge to know the clause was required.

```python
# ❌ mass assignment: the client picks its own role
user.update(**request.json)

# ✅ explicit allowlist of writable fields
ALLOWED = {"display_name", "timezone", "locale"}
user.update(**{k: v for k, v in request.json.items() if k in ALLOWED})
```

### SSRF and Outbound Requests

Any feature that fetches a user-supplied URL — webhooks, avatar import, PDF
rendering, link previews — reaches your internal network and cloud metadata
endpoints unless it is constrained.

```python
# ❌ fetches anything: http://169.254.169.254/, http://localhost:6379/, file://
requests.get(request.json["url"])

# ✅ scheme allowlist, resolved IP checked against private ranges,
#    redirects off so a 302 cannot re-target the request
import ipaddress, socket, requests
from urllib.parse import urlparse

url = urlparse(candidate)
if url.scheme not in ("http", "https"):
    raise ValueError
ip = ipaddress.ip_address(socket.gethostbyname(url.hostname))
if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
    raise ValueError
requests.get(candidate, allow_redirects=False, timeout=5)
```

Checking the hostname without resolving it misses DNS names that simply point at
`127.0.0.1`. Allowing redirects hands the attacker a second, unchecked fetch.

### Reviewing the Change in Context

A diff is a poor unit of security review. It reliably surfaces line-level defects
and reliably hides:

- **Reachability changes** — an existing internal handler newly wired to a public route
- **Invariant erosion** — a validation moved earlier, leaving a second caller unguarded
- **Aggregate exposure** — three benign fields added across three PRs that together
  identify a user

For changes touching authentication, authorization, tenancy, payments, file
handling, or cryptography, review the whole flow: entry point, middleware chain,
handler, data access, response serializer. Elsewhere the diff is enough. Design-level
questions — is this trust boundary in the right place at all — belong to
`security-architecture-review`, not here.

## Common Anti-Patterns

❌ **Blocklist filtering** — stripping `<script>`, rejecting `'` and `--`.
Encodings, casing, and nesting defeat it.
✅ Structural safety: parameterized queries, contextual escaping, argv lists.

❌ **Trusting client-side validation** — price, quantity, role, and `is_admin`
arriving from the browser.
✅ Re-derive every security-relevant value server-side from authoritative state.

❌ **Checking ownership after the fetch** — `obj = get(id)` then `if obj.owner != me`.
Survives until someone adds an early return, a log line, or a cache write above it.
✅ Make ownership part of the query predicate.

❌ **Swallowing exceptions around security decisions** — `except Exception: pass`
turns a failed permission lookup into an allow.
✅ Fail closed; let the request 500 rather than proceed unauthorized.

❌ **Comparing secrets with `==`** — leaks length and prefix through timing.
✅ `hmac.compare_digest(expected, provided)`.

❌ **Approving because static analysis was clean** — SAST cannot know this row
belongs to another tenant. That gap is the reviewer's whole job; see
`security-testing-strategies` for what each tool structurally cannot find.
✅ Treat tooling as coverage for the mechanical classes only.

❌ **Reviewing only application code** — CI configs, Dockerfiles, IaC, and
migrations carry credentials and permission grants too.
✅ Keep them in scope; a `chmod 777` or a wildcard IAM action is a finding.

## Secure Code Review Checklist

- [ ] Every user-controlled value traced from source to sink
- [ ] All SQL parameterized; dynamic identifiers allowlisted
- [ ] No `shell=True`, `eval`, `pickle.loads`, or `yaml.load` on external input
- [ ] Output escaped for its context (HTML body, attribute, JS, URL)
- [ ] Object-level ownership enforced inside the query, on reads and writes
- [ ] Write endpoints use a field allowlist — no mass assignment
- [ ] File paths resolved and confined to a base directory
- [ ] User-supplied URLs: scheme allowlist, resolved-IP check, redirects off, timeout set
- [ ] Secrets from environment or vault, never literals; no secrets in logs
- [ ] CSPRNG for all tokens; `compare_digest` for all secret comparisons
- [ ] Rate limits on login, reset, invite, and any send-email path
- [ ] CSRF protection on cookie-authenticated state-changing requests
- [ ] Error handling fails closed; no bare `except` around authorization
- [ ] Auth, tenancy, payment, and upload changes reviewed as whole flows
- [ ] New endpoints covered by a test asserting 403 on another tenant's id
- [ ] CI config, Dockerfiles, IaC, and migrations included in review scope
