# Authentication Design (Verbose)

## Core Patterns

### Password Storage

Authentication starts with never holding the secret you are checking. Store a
verifier — a slow, salted hash — not the password.

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()          # argon2id: memory-hard, salt embedded in output

def register(email: str, password: str) -> None:
    db.insert(email=email, password_digest=ph.hash(password))

def check(email: str, password: str) -> bool:
    row = db.find(email)
    if row is None:
        ph.hash("dummy")       # burn equivalent time so timing can't enumerate
        return False
    try:
        ph.verify(row.password_digest, password)
    except VerifyMismatchError:
        return False
    if ph.check_needs_rehash(row.password_digest):
        db.update(email, password_digest=ph.hash(password))   # transparent upgrade
    return True
```

| Algorithm | Verdict | Note |
|---|---|---|
| argon2id | Preferred | Memory-hard; resists GPU and ASIC |
| bcrypt (cost ≥ 12) | Fine | Ubiquitous; 72-byte input cap |
| scrypt | Fine | Memory-hard, tuning is fiddly |
| PBKDF2 | Legacy-only | Acceptable only where FIPS demands it |
| sha256 / md5 | Never | Fast by design — precisely wrong |

`check_needs_rehash` matters: it lets you raise cost parameters over time and
upgrade each user's digest silently on their next successful login.

### Session Management

```python
import secrets

def start_session(user_id: int) -> str:
    sid = secrets.token_urlsafe(32)        # 256 bits of entropy
    cache.setex(f"sess:{sid}", 1209600, user_id)   # 14d, server-side
    return sid
```

Return it with the flags that make it hard to steal:

```
Set-Cookie: session=<sid>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=1209600
```

Rotate the identifier on every privilege change — login, password change, role
elevation. Without rotation you are open to session fixation, where an attacker
plants a known session id before the victim authenticates.

### Sessions vs Tokens

| Dimension | Server-side session | JWT |
|---|---|---|
| Revocation | Delete the key — instant | Not possible before expiry |
| Horizontal scale | Needs shared store | None needed |
| Payload visible to client | No | Yes (base64, not encrypted) |
| Size on the wire | ~40 bytes | 500 bytes–2 KB |
| Failure mode | Store outage logs everyone out | Stolen token valid until expiry |

JWTs are frequently chosen for statelessness and then given a revocation list —
which reintroduces the shared store and forfeits the only advantage. If you need
revocation, use sessions.

When you do use JWTs:

```python
jwt.decode(
    token,
    key,
    algorithms=["RS256"],          # pin it — never trust the header's alg
    audience="api.example.com",    # verify aud
    issuer="auth.example.com",     # verify iss
)
```

Pinning `algorithms` defeats the classic `alg: none` and RS256→HS256 confusion
attacks, where an attacker re-signs a token using the public key as an HMAC secret.

### Multi-Factor Authentication

| Factor | Phishing-resistant | Cost | Notes |
|---|---|---|---|
| WebAuthn / passkey | Yes | Low | Credential bound to origin — the strong default |
| TOTP (RFC 6238) | No | Low | Code is replayable within its window |
| Push approval | No | Medium | Vulnerable to MFA-fatigue prompting |
| SMS | No | Medium | SIM-swap; weakest, still better than nothing |

Enforce a single-use constraint on TOTP: cache the consumed `(user, code)` for
the step window, or an intercepted code is replayable for ~30 seconds.

### Account Recovery

Recovery is usually the weakest link — it is a second authentication path that
bypasses the first.

```python
raw = secrets.token_urlsafe(32)
db.insert_reset(
    user_id=user.id,
    token_hash=sha256(raw),        # store the hash; a DB leak must not grant resets
    expires_at=now() + timedelta(minutes=15),
    used=False,
)
send_email(user.email, f"https://example.com/reset?t={raw}")
```

Single-use, short-lived, hashed at rest, and invalidating every active session on
completion. Return the same response whether or not the address exists.

## Common Anti-Patterns

❌ **Distinguishing "no such user" from "wrong password"** — turns login into an
account enumeration oracle.
✅ One message, one timing profile, for every failure.

❌ **Rate-limiting per IP only** — credential stuffing arrives from thousands of
addresses, one attempt each.
✅ Limit per account and per IP, with exponential backoff.

❌ **Long-lived JWTs as the session** — a stolen token stays valid for days.
✅ Short access TTL (≤ 15 min) plus a refresh token you can revoke.

❌ **Rolling your own crypto or token format.**
✅ Use the platform's session machinery and a vetted library.

❌ **Trusting `alg` from the token header.**
✅ Pin the accepted algorithm list at verification time.

## Authentication Checklist

- [ ] Passwords hashed with argon2id / bcrypt (cost ≥ 12) / scrypt
- [ ] Rehash-on-login path in place for cost upgrades
- [ ] Session ids ≥ 128 bits from a CSPRNG
- [ ] `HttpOnly`, `Secure`, `SameSite` set on session cookies
- [ ] Session id rotated on login and privilege change
- [ ] Uniform response and timing for all login failures
- [ ] Rate limiting per account and per IP
- [ ] MFA available; WebAuthn offered where feasible
- [ ] TOTP codes single-use within their window
- [ ] Reset tokens hashed, single-use, ≤ 15 min TTL
- [ ] All sessions invalidated on password change
- [ ] JWT `alg`, `aud`, `iss` verified explicitly
