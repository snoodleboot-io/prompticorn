# API Security Hardening (Minimal)

## Purpose
Concrete configuration that shrinks an API's attack surface at the edge and in the runtime — transport, CORS, limits, headers, and egress.

## Core Techniques

### 1. Terminate TLS With a Modern Profile
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;                 # let TLS 1.3 clients choose
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
```
Drop TLS 1.0/1.1 outright. Add `preload` to HSTS only once every subdomain — including the legacy admin host — serves HTTPS; getting off the preload list takes months.

### 2. Configure CORS Explicitly, Never Reflectively
```python
# ❌ Reflecting Origin with credentials = any site can call your API as the user
headers["Access-Control-Allow-Origin"] = request.headers["Origin"]
headers["Access-Control-Allow-Credentials"] = "true"

# ✅ Static allowlist, exact string match
if origin in {"https://app.example.com", "https://admin.example.com"}:
    headers["Access-Control-Allow-Origin"] = origin
    headers["Vary"] = "Origin"
```
Browsers reject `Allow-Origin: *` when credentials are sent; teams "fix" that by reflecting the origin, which is strictly worse. CORS is also not authorization — it constrains browsers only, never curl.

### 3. Bound Every Request Dimension
| Limit | Typical value | Blocks |
|---|---|---|
| Body size | 1 MB (10 MB for uploads) | Memory exhaustion |
| Header size | 8 KB | Header stuffing |
| JSON nesting depth | 32 | Parser stack blowup |
| Page/array size | `limit <= 100` | Unbounded result sets |
| Request timeout | 10–30 s | Slowloris, hung upstreams |

Set `client_max_body_size 1m;` at the proxy *and* the same limit in the app — anything that reaches the pod directly bypasses the edge.

### 4. Rate-Limit in Layers
```nginx
limit_req_zone $binary_remote_addr zone=perip:10m rate=20r/s;
limit_req zone=perip burst=40 nodelay;
```
Edge/IP limits absorb floods; per-principal quotas inside the app protect expensive endpoints. Always return `429` with `Retry-After` — without it, clients retry immediately and convert a limit into an outage.

### 5. Send API-Appropriate Headers
```
Content-Type: application/json
X-Content-Type-Options: nosniff
Cache-Control: no-store
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```
Most HTML-oriented headers are noise on a JSON API; `nosniff` and `no-store` are not. `no-store` on authenticated responses keeps tokens and PII out of shared caches.

### 6. Constrain Egress and Runtime
Deny-by-default egress NetworkPolicy, `runAsNonRoot: true`, read-only root filesystem, all capabilities dropped. An SSRF or RCE that cannot dial out or reach the cloud metadata endpoint is a contained incident instead of a breach.

## Warning Signs

- `Access-Control-Allow-Origin` echoing the request's `Origin` header
- No body-size limit, or one configured only at the CDN
- `429` responses with no `Retry-After` — or no 429s at all under load testing
- TLS 1.0/1.1 or 3DES still negotiable (`nmap --script ssl-enum-ciphers -p 443 host`)
- Wildcard origin allowlists matched with `endswith("example.com")` — `evilexample.com` passes
- Containers running as uid 0 with unrestricted egress
- `/metrics`, `/debug/pprof`, or actuator endpoints bound to 0.0.0.0
- `Server:` / `X-Powered-By` headers advertising exact framework versions
