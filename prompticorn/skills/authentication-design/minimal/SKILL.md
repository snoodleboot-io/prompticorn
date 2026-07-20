# Authentication Design (Minimal)

## Purpose
Design authentication that proves who a user is, without leaking credentials or sessions.

## Core Techniques

### 1. Never Store Passwords — Store Hashes
```python
# ✅ Memory-hard KDF with a per-password salt (built in)
from argon2 import PasswordHasher
ph = PasswordHasher()                    # argon2id, sane defaults
digest = ph.hash(password)               # store this
ph.verify(digest, submitted)             # raises on mismatch

# ❌ Never: md5/sha1/sha256 of a password — GPUs do ~10^10 sha256/sec
```
bcrypt (cost ≥ 12) and scrypt are acceptable alternatives. The SHA family is not: it is fast by design, which is exactly wrong here.

### 2. Pick Session Cookies or Tokens Deliberately
| | Session cookie | JWT / bearer token |
|---|---|---|
| Revocation | Immediate (delete server-side) | Hard — valid until expiry |
| State | Server holds it | Self-contained |
| Best for | Browser apps, one origin | Service-to-service, short TTL |

Default to server-side sessions for browser apps. Reach for JWTs when you genuinely need statelessness, and keep TTLs short (≤ 15 min) with a refresh token.

### 3. Set Cookie Flags
```
Set-Cookie: session=<opaque-random>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=1209600
```
- `HttpOnly` — JavaScript cannot read it, blunting XSS session theft
- `Secure` — never sent over plaintext HTTP
- `SameSite=Lax` — blocks the common CSRF shapes

The value must be high-entropy random (≥ 128 bits), never a user id or anything guessable.

### 4. Make Login Responses Uniform
```python
# ❌ Leaks which accounts exist
if not user:        return "No such user"
if not verify(pw):  return "Wrong password"

# ✅ Same message, same timing
if not user or not verify(pw):
    return "Invalid email or password"
```
Verify against a dummy hash when the user is absent, so a missing account and a wrong password take the same time.

### 5. Rate-Limit and Lock Out
Throttle per-account *and* per-IP. Per-IP alone misses credential stuffing from botnets; per-account alone lets one IP spray many accounts. Exponential backoff after ~5 failures.

### 6. Add a Second Factor
TOTP (RFC 6238) is the cheap default. WebAuthn/passkeys are stronger — phishing-resistant, because the credential is bound to the origin. SMS is the weakest common factor (SIM swap), but still beats no MFA.

## Warning Signs

- Passwords hashed with a fast algorithm, or stored reversibly
- Session id derived from user data, or missing `HttpOnly`
- Login errors that distinguish "no such user" from "wrong password"
- No rate limiting on the login endpoint
- JWTs with multi-day expiry and no revocation path
- Password reset tokens that don't expire or aren't single-use
