# Cryptography Fundamentals (Minimal)

## Purpose
Choose the right cryptographic primitive for a job, and use it with the parameters that make it safe. Never design your own.

## Core Techniques

### 1. Encrypt With AEAD, Not Raw Ciphers
Authenticated Encryption with Associated Data gives confidentiality *and* integrity in one step. Unauthenticated ciphertext is malleable — an attacker who cannot read it can still flip bits in it.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)                       # 96-bit nonce, MUST be unique per key
ct = aesgcm.encrypt(nonce, plaintext, b"user:42")   # 3rd arg = associated data
pt = aesgcm.decrypt(nonce, ct, b"user:42")          # raises InvalidTag if tampered
```

Store the nonce alongside the ciphertext — it is not secret, only unique.

### 2. Never Reuse a Nonce With AES-GCM
Nonce reuse under the same key is *catastrophic*, not merely weak. Two messages under the same (key, nonce) leak the XOR of their plaintexts and allow recovery of the GHASH authentication subkey — the attacker can then forge arbitrary valid ciphertexts for that key.

- Random 96-bit nonces are safe up to roughly 2^32 messages per key.
- If you cannot guarantee uniqueness, use XChaCha20-Poly1305 (192-bit nonce) or AES-GCM-SIV, which degrade gracefully on repeat.

### 3. Never Use ECB
ECB encrypts each block independently, so identical plaintext blocks produce identical ciphertext blocks. Structure survives encryption — the classic "encrypted penguin" is still recognisably a penguin. Use GCM, or CBC with a separate HMAC if a legacy protocol forces it.

### 4. Match the Hash to the Job
| Need | Use | Not |
|---|---|---|
| Content integrity / digest | SHA-256, SHA-3, BLAKE2 | MD5, SHA-1 (collisions are practical) |
| Password verifier | argon2id, bcrypt, scrypt | any plain hash |
| Keyed integrity | HMAC-SHA256 | `sha256(key + msg)` |
| Derive keys from a key | HKDF | ad-hoc concatenation |

Passwords need a *slow, memory-hard* function; a GPU does on the order of 10^10 SHA-256/sec.

### 5. Use Asymmetric Crypto for Key Agreement and Signing
```python
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

priv = X25519PrivateKey.generate()
shared = priv.exchange(peer_public_key)      # raw DH output — NOT a key yet
key = HKDF(algorithm=SHA256(), length=32, salt=None,
           info=b"handshake v1").derive(shared)
```
Always run the raw shared secret through a KDF: it is not uniformly random. Use X25519 for key agreement, Ed25519 for signatures, RSA (≥ 3072-bit, OAEP/PSS — never PKCS#1 v1.5) only for interop.

### 6. Get Randomness From the OS CSPRNG
`os.urandom` / `secrets` (Python), `crypto.randomBytes` (Node), `crypto/rand` (Go). Never `random`, `Math.random`, `rand()`, or a timestamp seed — those are predictable from a handful of outputs.

### 7. Compare Secrets in Constant Time
```python
import hmac
hmac.compare_digest(expected_mac, provided_mac)   # not ==
```
`==` short-circuits on the first differing byte, leaking the match length through timing.

## Warning Signs

- A counter, timestamp, or fixed value used as an AES-GCM nonce
- `AES.new(key, AES.MODE_ECB)` anywhere in the codebase
- MD5 or SHA-1 used for anything security-relevant
- A raw ECDH/X25519 output used directly as an encryption key
- Encryption with no authentication tag or MAC (CBC or CTR alone)
- Custom "encryption" built from XOR, base64, or a home-grown cipher
- Keys or IVs hardcoded in source, or committed to git
- `==` used to compare tokens, MACs, or signatures
- RSA with PKCS#1 v1.5 padding, or keys under 2048 bits
