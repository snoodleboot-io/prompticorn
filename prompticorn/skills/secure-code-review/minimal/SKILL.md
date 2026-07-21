# Secure Code Review (Minimal)

## Purpose
Read code as an attacker would, at the line level, and find the flaws scanners
structurally cannot see — missing authorization, broken business logic, misused crypto.

## Core Techniques

### 1. Follow Untrusted Input to Its Sink
Trace every value the user controls until it reaches something dangerous: a query,
a shell, a file path, an HTTP client, a deserializer, a template.

```python
# ❌ String-built SQL — the classic injection sink
db.execute(f"SELECT * FROM users WHERE email = '{email}'")

# ✅ Parameterized — driver sends query and data separately
db.execute("SELECT * FROM users WHERE email = %s", (email,))
```
Parameterization is not escaping. Escaping is a filter you can outsmart;
parameterization means the value never enters the parser as syntax.

### 2. Check Authorization at Every Object Access
Authentication answers *who*; authorization answers *may they touch this row*.
Missing object-level checks (IDOR) are the single most common finding in review
and the one no scanner reliably flags, because the code is syntactically perfect.

```python
# ❌ Authenticated, but any user can read any invoice
@login_required
def get_invoice(request, invoice_id):
    return Invoice.objects.get(id=invoice_id)

# ✅ Ownership is part of the lookup, not a later branch
    return Invoice.objects.get(id=invoice_id, org_id=request.user.org_id)
```
Push the tenancy predicate into the query. A check performed after the fetch
gets forgotten on the next endpoint someone adds.

### 3. Read the Whole Flow, Not Just the Diff
A diff shows what changed, not what the change now makes reachable. A three-line
patch adding a new route can expose a handler written for internal use. For any
change touching auth, money, tenancy, or file handling, open the surrounding
call chain and ask what else now reaches the modified code.

### 4. Interrogate Every Crypto and Randomness Call
```python
import random, secrets
random.choice(chars)          # ❌ Mersenne Twister — predictable from ~624 outputs
secrets.token_urlsafe(32)     # ✅ CSPRNG
```
Also flag: `==` comparing secrets (use `hmac.compare_digest`), AES-ECB, static or
reused IVs, decryption without an authentication tag, and homemade token formats.

### 5. Look for What Isn't There
The vulnerability is usually an absence: no rate limit on the reset endpoint, no
`CSRF` token on a state-changing POST, no size cap before the upload buffer, no
timeout on the outbound HTTP call, no ownership filter, no re-check of price
server-side after the client submits the cart.

### 6. Treat Error Paths and Defaults as Attack Surface
Fail closed. `except Exception: pass` around a permission check turns a denial
into an allow. A config default of `DEBUG=True` or `verify=False` in a shared
helper ships to production far more often than the equivalent explicit line.

## Warning Signs

- Query strings assembled with f-strings, `+`, or `%` on request data
- `subprocess` with `shell=True`, or `eval` / `pickle.loads` on external input
- A resource fetched by id with no tenant or owner predicate in the query
- Secrets, tokens, or connection strings literal in source or committed config
- `verify=False`, disabled certificate checks, or a bare `except` around authz
- Authorization decided in the frontend, or trusted from a client-supplied field
- `random` used for tokens, ids, passwords, or nonces
- New endpoint added without a matching test that asserts a 403 for a foreign id
