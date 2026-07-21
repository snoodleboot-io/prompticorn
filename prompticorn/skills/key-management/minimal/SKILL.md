# Key Management (Minimal)

## Purpose
Manage the lifecycle of encryption keys — generation, storage, rotation, revocation — so that a key compromise is survivable and rotation does not require re-encrypting the world.

## Core Techniques

### 1. Use Envelope Encryption
Encrypt data with a per-record Data Encryption Key (DEK); encrypt the DEK with a Key Encryption Key (KEK) that never leaves the KMS/HSM.

```python
# Encrypt
resp = kms.generate_data_key(KeyId="alias/app-kek", KeySpec="AES_256")
dek_plain, dek_wrapped = resp["Plaintext"], resp["CiphertextBlob"]
nonce = os.urandom(12)
ct = AESGCM(dek_plain).encrypt(nonce, plaintext, record_id.encode())
del dek_plain                              # drop it as soon as you are done
store(record_id, wrapped_key=dek_wrapped, nonce=nonce, ciphertext=ct)

# Decrypt
dek_plain = kms.decrypt(CiphertextBlob=row.wrapped_key)["Plaintext"]
```

Why: bulk data never travels to the KMS (fast, cheap, no size limit), the KEK never reaches your process, and rotating the KEK means re-wrapping small DEKs rather than re-encrypting terabytes.

### 2. Never Let Keys Touch Disk or Git
Generate inside the KMS/HSM where possible. If a key must exist in your process, keep it in memory only, and never log, print, or serialize it into an error report.

```bash
git log --all -p -S 'BEGIN PRIVATE KEY' | head    # check before you claim it's clean
```

### 3. Version Keys and Store the Version With the Ciphertext
```json
{"kv": 3, "alg": "AES-256-GCM", "nonce": "…", "ct": "…"}
```
Without a version tag, rotation is impossible: you cannot tell which key decrypts which row. Decrypt with the key the record names; encrypt with the current one.

### 4. Rotate on a Schedule and on Compromise
| Key type | Typical rotation | Notes |
|---|---|---|
| KMS KEK | 1 year (automatic) | Re-wrap DEKs; data untouched |
| DEK | Per record / per object | Effectively never reused |
| TLS certificate | 90 days or less | Automate with ACME |
| Signing key | 6–12 months | Publish both keys during overlap |

Rotation must be a routine, exercised path — a rotation procedure you have never run is not a control, and it is the thing you will need under pressure during an incident.

### 5. Overlap Old and New Keys During Rollout
Deploy the new key as *accepted* before making it *active*. For signing: publish both public keys (e.g. two entries in a JWKS with distinct `kid`) and keep verifying with the old one until every issued token has expired. Flipping in one step breaks in-flight requests.

### 6. Separate Keys by Purpose and Environment
One key per (purpose, environment, tenant boundary). A single key encrypting sessions, database columns, and backups turns one leak into total compromise. Production keys must be inaccessible from staging — separate accounts or projects, not just separate names.

### 7. Restrict and Audit Key Use
Grant `kms:Decrypt` to the specific role that needs it, not `kms:*` to the account. Every KMS call is logged: alert on decrypt volume spikes, decrypts from unexpected roles or regions, and any `ScheduleKeyDeletion`.

## Warning Signs

- Private keys or `.pem` files in the repository, container image, or CI config
- One key encrypting everything, across all environments
- Ciphertext with no key-version or algorithm field
- A rotation procedure documented but never executed
- Keys "rotated" by deleting the old one, orphaning existing ciphertext
- Application code calling KMS `Encrypt` on multi-MB payloads instead of using data keys
- DEK plaintext cached indefinitely, or written to a log or crash dump
- `kms:*` or `Resource: "*"` in an IAM policy
- No alerting on key deletion or on decrypt-rate anomalies
