# Edge And CDN Delivery (Minimal)

## Purpose
Serve content from the edge so it is fast and cheap — which depends entirely on getting cache headers, keys, and invalidation right, not on merely turning a CDN on.

## Core Techniques

### 1. A CDN Without Correct Cache Headers Does Nothing
The CDN obeys origin headers. If the origin sends `Cache-Control: no-store` (or nothing, and the CDN defaults conservative), every request falls through to origin and you have added a hop, not removed load. Correctness lives in the headers, not the toggle.
```
# Immutable, fingerprinted asset (app.a1b2c3.js) — cache hard, forever
Cache-Control: public, max-age=31536000, immutable

# HTML that changes — let the edge cache but revalidate
Cache-Control: public, s-maxage=60, stale-while-revalidate=600
```
`s-maxage` targets the CDN specifically; `max-age` targets the browser. Set them separately.

### 2. Fingerprint Assets, Version HTML
Give static assets content-hashed names so they can cache forever and a deploy simply references new URLs. Keep the HTML entry point short-lived so clients pick up the new references. This avoids invalidation for the bulk of your bytes.

### 3. Control the Cache Key
The cache key decides what counts as "the same object". Strip query params that do not change the response (tracking tags) or every `?utm=...` becomes a separate miss. Only `Vary` on headers that genuinely change the body (e.g. `Accept-Encoding`); `Vary: Cookie` or `Vary: User-Agent` shatters the cache into near-uniqueness.

### 4. Prefer Versioning to Invalidation
Invalidation (purge) is slow to propagate, sometimes rate-limited, and eventually consistent across edge locations. Design so you rarely need it: fingerprinted assets need no purge. Reserve purges for emergencies (a leaked or wrong response), not routine deploys.

### 5. Use `stale-while-revalidate` and Origin Shielding
- `stale-while-revalidate` serves the slightly-stale copy instantly while refreshing in the background — users never wait on origin.
- A shield/tiered cache designates one mid-tier that talks to origin, so a cold object is fetched once, not once per edge PoP (which would be a thundering herd on origin).

### 6. Push Logic to the Edge Only When It Belongs There
Edge compute (CDN functions/workers) fits request rewriting, auth checks, header manipulation, A/B routing, and personalization at the boundary. It is not a place for heavy compute or a database — edge runtimes are constrained (short CPU budget, limited APIs) and far from your data. Route and shape requests at the edge; do the real work at origin.

### 7. Measure Offload, Don't Assume It
The only proof a CDN is working is the numbers: edge cache-hit ratio and the drop in origin request volume and egress. A high hit ratio on assets but a low one on HTML usually points at a cache-key or `Vary` problem, not a CDN that "isn't caching". Watch hit rate per content type, and treat a sudden dip as a header regression to investigate.

## Warning Signs
- "We added a CDN" but the origin still sees the same request volume
- Assets served without fingerprints, forcing purges on every deploy
- `Cache-Control` absent, so behavior depends on the CDN's default
- `Vary: Cookie` / `Vary: User-Agent`, or unstripped query params, collapsing hit rate
- Routine deploys that depend on cache purges propagating in time
- A cold cache hammering origin with no shield/tiered cache in front
- Edge functions reaching back to a database or doing heavy computation
