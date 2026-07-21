# API Versioning Strategy (Minimal)

## Purpose
Evolve an API without breaking clients you do not control, and retire old shapes on a schedule instead of by surprise.

## Core Techniques

### 1. Know What Actually Breaks

| Change | Breaking? |
|---|---|
| Add an optional request field | No |
| Add a response field | No — if clients ignore unknowns |
| Remove or rename a response field | Yes |
| Make an optional request field required | Yes |
| Tighten validation on an existing field | Yes |
| Change a default value | Yes — silently |
| Add a value to an existing response enum | Yes, in practice |

The last two are the ones teams get wrong. A new enum member breaks every client with an exhaustive `switch` and no default branch, and a changed default rewrites behavior for callers who never touched the field.

### 2. Version in the URI

```
GET /v1/orders/8812        # visible in logs, curl, cache keys, bug reports

GET /orders/8812           # "purer" — and worse in practice
Accept: application/vnd.acme.v1+json
```

Header versioning is architecturally cleaner: the URI names the resource, the header negotiates the representation. It also makes every cache key depend on a header you must remember to add to `Vary`, hides the version from access logs, and makes reproducing a bug report require the reporter's headers. Choose URI versioning unless you have a specific reason not to.

Version the whole API, not per-endpoint. `/v1/orders` alongside `/v3/customers` is a matrix nobody can reason about.

### 3. Expand, Migrate, Contract

Never rename in place. Three deploys, not one:

1. **Expand** — add `full_name` alongside `name`; write both, accept either.
2. **Migrate** — backfill, move clients, count reads of the legacy field.
3. **Contract** — remove `name` only once that counter has been zero for longer than your slowest client's release cycle.

Expand and contract must be separate releases. Combined, they are a rename, and a rename has no rollback: old clients start failing the moment it ships, and reverting does not un-break the requests already served.

### 4. Deprecate With Headers and a Date

```http
HTTP/1.1 200 OK
Deprecation: Sun, 01 Nov 2026 00:00:00 GMT
Sunset: Wed, 01 Apr 2027 00:00:00 GMT
Link: <https://api.acme.com/docs/v2-migration>; rel="deprecation"
```

`Sunset` (RFC 8594) names the moment the resource stops answering. Give external clients 6–12 months, and schedule a brownout — a short, announced window of `410 Gone` — so stragglers discover the dependency while there is still time. A changelog post is not a deprecation notice.

### 5. Instrument Version Usage

Label the request metric with version and client, or you will never be allowed to delete anything:

```
http_requests_total{api_version="v1", client_id="mobile-ios", endpoint="/orders"}
```

Sunset then becomes a list of accounts to email rather than an argument about who might be affected.

### 6. Reject Unknown Request Fields

Silently dropping an unrecognized field turns a client's typo into your production incident six months later, when you add a real field by that name. Return 400 and name the offending field.

## Warning Signs

- Enum values added to a live response with no version bump
- A field renamed in a single deploy
- Deprecation announced only in a changelog, with no `Sunset` header or date
- Per-endpoint versions drifting independently
- No metric that answers "who is still on v1?"
- More than two major versions live at once
- Old versions maintained as a forked codebase rather than a translation layer
- "No one uses that field" asserted with no telemetry behind it
