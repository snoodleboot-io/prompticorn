# API Security Hardening (Verbose)

## Core Patterns

### Transport Configuration

TLS is either configured deliberately or inherited from a distro default written
years ago. Pin the protocol floor and let 1.3 negotiate its own suites.

```nginx
server {
    listen 443 ssl;
    http2 on;

    ssl_protocols             TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers               ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305;
    ssl_session_tickets       off;      # tickets weaken forward secrecy if keys are static
    ssl_stapling              on;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    server_tokens off;                  # drop the version from Server:
}
```

Two details that bite. First, `add_header` in nginx does not inherit into a
`location` block that declares its own `add_header` — headers silently vanish on
exactly the routes people customize; `always` covers error responses but not
that inheritance rule. Second, HSTS `preload` is a one-way door: browsers ship
the list in-binary, so a subdomain that cannot do HTTPS becomes unreachable for
release cycles.

Verify from outside rather than from the config file:

```bash
nmap --script ssl-enum-ciphers -p 443 api.example.com
openssl s_client -connect api.example.com:443 -tls1_1   # must fail to negotiate
```

### Cross-Origin Policy

```python
ALLOWED = frozenset({"https://app.example.com", "https://admin.example.com"})

@app.middleware("http")
async def cors(request, call_next):
    origin = request.headers.get("origin")
    resp = await call_next(request)
    if origin in ALLOWED:                       # exact match against a frozen set
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Vary"] = "Origin"         # or a cache serves one tenant's header to another
    return resp
```

| Mistake | Why it fails |
|---|---|
| `Allow-Origin: *` with credentials | Browser refuses; teams then reflect the origin |
| Reflecting any `Origin` | Every website becomes a trusted caller of the user's session |
| `origin.endswith(".example.com")` | `evil-example.com` and `example.com.attacker.io` slip through |
| Omitting `Vary: Origin` | CDN caches the header for the wrong origin |
| `Allow-Origin: null` | Sandboxed iframes and `data:` URLs send `Origin: null` |

Note the null-origin case specifically: it is reachable from any attacker page
via a sandboxed iframe, so `null` must never be in the allowlist.

### Request Limits and Timeouts

Every unbounded dimension is a denial-of-service primitive.

```nginx
client_max_body_size    1m;
client_header_buffer_size 8k;
large_client_header_buffers 4 8k;
client_body_timeout     10s;
client_header_timeout   10s;
send_timeout            30s;
keepalive_timeout       65s;
```

Mirror these in the application — the proxy is not the only ingress path:
service-mesh sidecars, port-forwards, and internal callers hit the pod directly.

```python
@app.get("/orders")
def list_orders(limit: int = Query(50, ge=1, le=100), cursor: str | None = None):
    ...          # a caller-controlled limit with no ceiling is a full table export
```

Decompression is the asymmetric case. Accepting gzipped request bodies means a
1 MB body can expand to gigabytes; cap the *decompressed* size and abort mid-
stream rather than trusting the compressed length.

### Rate Limiting and Quotas

Run the counter in a shared store, evaluated atomically — a per-instance
in-memory limiter multiplies the effective limit by your replica count, so a
"100 r/s" rule admits 1000 r/s across ten pods. In Redis, that means a Lua
script or `INCR` + `EXPIRE` in one round trip, never read-then-write.

Respond so clients can cooperate:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
RateLimit-Limit: 1000
RateLimit-Remaining: 0
RateLimit-Reset: 30
```

Choose the key by what you are protecting: API key or user id for quota
fairness, IP for anonymous floods, and the *account* for credential attacks.
Behind a proxy, `$remote_addr` is the proxy — key on a trusted-parsed
`X-Forwarded-For` and count from the right, or all clients share one bucket.

### Runtime and Egress Isolation

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"] }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-egress }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: ["Egress"]
  egress:
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
    - to: [{ namespaceSelector: { matchLabels: { name: kube-system } } }]
      ports: [{ port: 53, protocol: UDP }]
```

The default `Egress: {}` in Kubernetes is allow-all; a NetworkPolicy with an
empty egress list denies everything, including DNS — which is why the resolver
rule above is explicit and why the first attempt at this always breaks name
resolution. On AWS, also require IMDSv2 (`HttpTokens: required`) and set the hop
limit to 1 so a container cannot reach the node's credentials.

## Common Anti-Patterns

❌ **Reflecting the `Origin` header with `Allow-Credentials: true`.**
✅ Exact-match allowlist plus `Vary: Origin`.

❌ **Limits only at the CDN or ingress.**
✅ Enforce body size, timeouts, and pagination caps in the service itself.

❌ **Rate limiting on `$remote_addr` behind a load balancer.**
✅ Parse `X-Forwarded-For` from the right, past trusted proxy hops.

❌ **`429` with no `Retry-After`** — clients hot-loop and amplify the incident.
✅ Return `Retry-After` and `RateLimit-*` headers.

❌ **Copying an HTML security-header bundle onto a JSON API** — a long CSP on
`application/json` is cargo cult.
✅ `nosniff`, `no-store`, and `default-src 'none'` are the ones that earn their bytes.

❌ **Allow-all egress from application pods.**
✅ Deny by default; enumerate the destinations, DNS included.

## Hardening Checklist

- [ ] TLS 1.2 minimum; 1.0/1.1 and 3DES/RC4 confirmed unavailable externally
- [ ] HSTS `max-age >= 1 year`; `preload` only after subdomain audit
- [ ] CORS origins exact-matched from a static set; `null` never allowed
- [ ] `Vary: Origin` on every CORS response
- [ ] Body, header, nesting-depth, and decompressed-size limits set
- [ ] Read/write/idle timeouts configured at proxy and application
- [ ] Pagination has a server-side maximum the client cannot raise
- [ ] Rate limits keyed by principal and by IP, with `Retry-After` on 429
- [ ] `X-Content-Type-Options: nosniff` and `Cache-Control: no-store` on API responses
- [ ] `Server`/`X-Powered-By` version strings suppressed
- [ ] Containers non-root, read-only rootfs, `capabilities: drop: [ALL]`
- [ ] Default-deny egress NetworkPolicy with DNS explicitly permitted
- [ ] Cloud metadata service requires session tokens (IMDSv2) with hop limit 1
- [ ] Admin, metrics, and profiling endpoints on a non-public listener
- [ ] TLS and header configuration verified by an external scan in CI, not by review
