# Cryptography Fundamentals (Verbose)

## Core Patterns

### Choosing a Primitive

Cryptography rarely fails at the primitive — it fails at the seams, in how the
pieces are wired together. Name the property you need, then pick the primitive
that provides exactly that.

| Property needed | Primitive | Concrete choice |
|---|---|---|
| Confidentiality + integrity, shared key | AEAD cipher | AES-256-GCM, ChaCha20-Poly1305 |
| Integrity only, shared key | MAC | HMAC-SHA256 |
| Integrity + non-repudiation | Signature | Ed25519 |
| Agree a key over a public channel | Key exchange | X25519 |
| Turn a shared secret into keys | KDF | HKDF-SHA256 |
| Turn a password into a key | Password KDF | argon2id |
| Fingerprint content | Hash | SHA-256, BLAKE2b |

Note what is *not* on that list: encryption alone. Confidentiality without
integrity is almost never what you want, and unauthenticated ciphertext is the
root of padding-oracle, bit-flipping, and truncation attacks going back decades.

### Symmetric Encryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)

def seal(key: bytes, plaintext: bytes, context: bytes) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext, context)
    return nonce + ct              # the nonce is public — ship it with the ciphertext

def unseal(key: bytes, blob: bytes, context: bytes) -> bytes:
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(key).decrypt(nonce, ct, context)   # InvalidTag on any tampering
```

The `context` argument is Associated Data: authenticated but not encrypted. Bind
it to where the ciphertext belongs — a row id, a tenant id, a field name. Without
it, an attacker who can move ciphertexts between records can swap your account
balance for someone else's and every tag still verifies.

| Cipher | Nonce | Prefer when |
|---|---|---|
| AES-256-GCM | 96-bit | AES-NI hardware present (most servers); FIPS contexts |
| ChaCha20-Poly1305 | 96-bit | No AES hardware — mobile, embedded; constant-time in software |
| XChaCha20-Poly1305 | 192-bit | Random nonces at high volume, or uniqueness is hard to prove |
| AES-GCM-SIV | 96-bit | Nonce reuse is plausible and must not be fatal |

### Why Nonce Discipline Dominates

GCM is a counter mode: the keystream is a function of (key, nonce). Encrypting
two plaintexts under the same pair yields `C1 ⊕ C2 = P1 ⊕ P2`, which surrenders
both plaintexts to anyone with a little language modelling. Worse, the GHASH
authenticator is a polynomial whose key becomes recoverable from two tags sharing
a nonce — after which the attacker forges valid ciphertexts at will. This is the
single most common catastrophic misuse in production code, and it is a total
break, not a degradation.

Random 96-bit nonces are fine to roughly 2^32 messages per key (birthday bound).
A monotonic counter is safe only if it is durable across restarts and never
shared between writers — two replicas holding the same key, each counting from
zero, is the classic incident shape. Often the cleanest answer is to rotate the
key rather than track the counter; see the key-management skill for envelope
encryption and per-record data keys.

### Hashing and Key Derivation

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256

# One high-entropy secret -> several independent, purpose-bound keys
def subkey(master: bytes, purpose: bytes) -> bytes:
    return HKDF(algorithm=SHA256(), length=32,
                salt=tenant_salt, info=purpose).derive(master)

record_key = subkey(master, b"v1/record-encryption")
index_key  = subkey(master, b"v1/index-blinding")
```

Distinct `info` strings produce cryptographically independent keys, so a
compromise in one subsystem does not hand over the others. Version the `info`
string — it becomes your migration handle later.

Passwords are the exception. They are low-entropy, so they need a deliberately
expensive, memory-hard KDF — argon2id via `argon2.PasswordHasher`, not HKDF.

### Asymmetric Crypto

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

signing_key = Ed25519PrivateKey.generate()
sig = signing_key.sign(message)                   # 64 bytes, deterministic
signing_key.public_key().verify(sig, message)     # InvalidSignature on failure
```

Ed25519 derives its per-signature nonce deterministically from the key and
message, so it does not fail catastrophically on bad randomness the way ECDSA
does — the PlayStation 3 signing-key extraction came from repeated ECDSA nonces.
Prefer Ed25519 wherever you control both ends.

| Algorithm | Purpose | Sizing |
|---|---|---|
| X25519 | Key agreement | 32-byte keys, ~128-bit security |
| Ed25519 | Signatures | 32-byte key, 64-byte signature |
| ECDSA P-256 | Signatures for interop (WebAuthn, JWT ES256) | Needs a solid RNG |
| RSA-OAEP | Encryption, legacy interop only | ≥ 3072-bit |
| RSA-PSS | Signatures, legacy interop only | ≥ 3072-bit |

Never encrypt bulk data with RSA — it can only encrypt less than a key-length of
bytes, and slowly. The standard pattern is hybrid: agree or wrap a symmetric key
asymmetrically, then encrypt the payload with an AEAD.

Key agreement output is never a key:

```python
shared = my_x25519_private.exchange(peer_public)   # a group element, not uniform bits
key = HKDF(algorithm=SHA256(), length=32, salt=None,
           info=b"v1/session").derive(shared)
```

### Randomness and Comparison

Key material, nonces, salts, and tokens come from the OS CSPRNG — `secrets` /
`os.urandom`, `crypto.randomBytes`, `crypto/rand`. General-purpose PRNGs
(`random`, `Math.random`, `rand()`) are reconstructible from a handful of outputs.

Compare secrets with `hmac.compare_digest`, not `==`. Equality short-circuits on
the first differing byte, leaking the matching prefix length through timing and
letting an attacker walk a MAC out one byte at a time.

## Common Anti-Patterns

❌ **Reusing an AES-GCM nonce across messages** — leaks the plaintext XOR and
enables unlimited forgery under that key.
✅ Random 96-bit nonce per message, or XChaCha20-Poly1305 / AES-GCM-SIV where
uniqueness cannot be guaranteed.

❌ **ECB mode** — each block is encrypted independently, so identical plaintext
blocks yield identical ciphertext blocks and document structure survives intact.
✅ An AEAD mode with a per-message nonce.

❌ **Encrypting without authenticating (CBC or CTR with no MAC)** — ciphertext is
malleable, and padding oracles recover plaintext byte by byte.
✅ AEAD, or encrypt-then-MAC with HMAC over the IV *and* the ciphertext.

❌ **`sha256(key + message)` as a MAC** — vulnerable to length extension on
Merkle–Damgård hashes.
✅ `hmac.new(key, message, sha256)`.

❌ **Using a raw X25519/ECDH output directly as an encryption key.**
✅ Run it through HKDF with a context-binding, versioned `info`.

❌ **Rolling your own construction** because the library "doesn't do quite what we
need".
✅ Reshape the problem to fit a vetted primitive, or adopt libsodium / Tink, which
expose only safe combinations by design.

## Cryptography Checklist

- [ ] Every encryption path uses an AEAD, or explicit encrypt-then-MAC
- [ ] Nonce uniqueness per key is provable — random 96-bit or an extended-nonce cipher
- [ ] No ECB mode anywhere in the codebase
- [ ] Associated data binds each ciphertext to its record, tenant, or field
- [ ] All key material, nonces, and salts come from the OS CSPRNG
- [ ] Shared secrets pass through HKDF with a versioned, purpose-bound `info`
- [ ] Passwords use argon2id / scrypt / bcrypt, never a plain hash
- [ ] MACs are HMAC, not hash-of-concatenation
- [ ] Secret comparisons are constant-time
- [ ] Signatures use Ed25519 where possible; RSA is ≥ 3072-bit with OAEP/PSS
- [ ] MD5 and SHA-1 absent from all security-relevant paths
- [ ] TLS 1.3 with certificate and hostname verification enabled on every client
- [ ] No hand-rolled primitives, modes, or padding schemes
- [ ] Algorithm and key version stored alongside ciphertext so migration is possible
