# Secret Management (Verbose)

## Core Patterns

### Workload Identity as the Root Secret

Every secret system faces the same bootstrap problem: to fetch a secret you need
a credential, which is itself a secret. The answer is not to store one, but to
have the platform attest to who the workload is.

```python
# Kubernetes + Vault: the projected ServiceAccount token is the only "secret",
# it is issued by the API server, audience-bound, and expires in minutes.
jwt = open("/var/run/secrets/tokens/vault-token").read()
client.auth.kubernetes.login(role="orders-api", jwt=jwt)
db = client.secrets.database.generate_credentials(name="orders-api")
```

The equivalents: IAM roles for EC2/ECS/Lambda, GCP workload identity, Azure
managed identity, GitHub OIDC for CI. All share the property that the credential
is minted for one workload, is short-lived, and cannot be copied to a laptop and
reused.

### Delivery: How the Secret Reaches the Process

| Mechanism | Leak surface | Notes |
|---|---|---|
| Direct API read at startup | Process memory only | Best; enables in-process refresh |
| tmpfs file, mode 0400 | Filesystem, container escape | Good; supports rotation without restart |
| Environment variable | `/proc/<pid>/environ`, crash dumps, `docker inspect`, child processes | Weak |
| CLI argument | `ps aux`, shell history, process accounting | Never |
| Baked into image layer | Anyone who can pull the image | Never |

The environment-variable case deserves emphasis because it is the default in most
tutorials. `/proc/<pid>/environ` is readable by any process running as the same
user, including sidecars in a shared PID namespace. APM agents and error trackers
routinely serialize the entire environment into a crash report and ship it to a
third party. And `subprocess.run(...)` hands the whole environment to a child by
default — your database password is now in an ImageMagick invocation.

Kubernetes `Secret` objects are base64 *encoding*, not encryption. Without
encryption-at-rest configured on etcd, and RBAC restricting `get secrets`, any
namespace-reader has them in plaintext.

### Dynamic Credentials

The strongest available control is to stop having long-lived credentials at all.

```bash
$ vault read database/creds/orders-api
lease_id     database/creds/orders-api/aB3...
lease_duration  1h
password     A1a-8x2Kq...
username     v-kube-orders-a-1721390400
```

Vault creates a real database user, hands it over with a lease, and revokes it
when the lease expires. Equivalents exist for AWS STS (`AssumeRole`), GCP
short-lived service account credentials, and cloud-native database IAM auth
(RDS IAM tokens are valid 15 minutes).

The asymmetry matters: with a 90-day static password, a leak is an incident with
an unbounded window and a rotation project attached. With a 1-hour dynamic
credential, the same leak is usually already dead by the time it is noticed, and
revocation is a single lease revoke rather than a coordinated deploy.

### Rotation Without Downtime

Rotation fails when a single credential must change at a single instant. Use two
slots and overlap them.

```python
# Verify webhooks against both secrets during the overlap window
def verify(body: bytes, sig: str) -> bool:
    return any(
        hmac.compare_digest(sig, hmac.new(s, body, sha256).hexdigest())
        for s in (settings.webhook_secret_current, settings.webhook_secret_previous)
    )
```

The general procedure:

1. Create credential B alongside the live credential A.
2. Deploy consumers that *accept* both. Wait for full rollout.
3. Switch producers/clients to use B.
4. Confirm zero usage of A — auth logs, KMS/DB audit logs, vendor dashboards.
5. Revoke A. Only now is rotation complete.

| Secret | Cadence | Mechanism |
|---|---|---|
| Database access | Continuous | Dynamic creds or IAM auth — no rotation event |
| Static DB password (legacy) | 90 days | Two alternating accounts |
| Third-party API key | 90 days | Most vendors support two live keys |
| Webhook signing secret | 180 days | Dual-verify during overlap |
| Service-to-service auth | Continuous | mTLS with short-lived certs |
| Any secret, post-exposure | Immediately | Rotate before cleanup, always |

Step 4 is the one teams skip, and it is why "rotation" so often causes the outage
it was supposed to prevent. Do not revoke on a schedule — revoke on evidence.

### Preventing Leaks

Layer the defences: a gitleaks pre-commit hook (fast, bypassable), CI scanning on
the full diff (not bypassable), and platform push protection (GitHub secret
scanning), which rejects the push outright. Detection-only scanning of history is
the weakest layer — by then the secret is already distributed.

In the application, make leaks structurally hard rather than a matter of
discipline:

```python
from pydantic import BaseModel, SecretStr

class Settings(BaseModel):
    db_password: SecretStr        # str(x) -> '**********'; .get_secret_value() to use

# Plus a defensive log filter for the ones that slip through other paths
PATTERNS = [r"AKIA[0-9A-Z]{16}", r"gh[pousr]_[A-Za-z0-9]{36}",
            r"sk-[A-Za-z0-9]{20,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]
```

### Exposure Response

A committed secret is compromised the moment it is pushed. Public repos are
scraped by bots within seconds — AWS keys in public GitHub are typically abused
for crypto mining in under five minutes. Even in a private repo, the object
survives in forks, clones, CI caches, and backups, and `git filter-repo` reaches
none of those.

Order of operations, always: **revoke or rotate first**, then investigate scope
through audit logs, then optionally rewrite history. Teams that reverse the first
two steps spend an hour on git surgery while the key is still live.

## Common Anti-Patterns

❌ **Secrets committed to the repository** — including `.env` files, `.tfvars`,
Helm values, and Kubernetes manifests.
✅ Runtime resolution from a secret broker, authenticated by workload identity.

❌ **Rewriting git history and calling the leak handled** — forks, clones, and CI
caches still hold the object.
✅ Rotate the credential first; treat history cleanup as optional hygiene.

❌ **Injecting credentials as environment variables** — exposed via
`/proc/<pid>/environ`, crash dumps, `docker inspect`, and inherited by every child
process.
✅ tmpfs file mounts with mode 0400, or a direct API read into process memory.

❌ **Passing a secret as a CLI flag** — permanently visible in `ps aux` and shell
history.
✅ stdin, or a file path argument.

❌ **Treating a Kubernetes `Secret` as encrypted** — it is base64 in etcd.
✅ Enable etcd encryption at rest, lock down RBAC, or use an external store via
the Secrets Store CSI driver.

❌ **One shared credential across services and environments** — no blast-radius
containment and no attribution in audit logs.
✅ A distinct identity per service per environment.

❌ **Revoking the old credential on a fixed date** rather than on evidence of
zero usage, or leaving standing human access to production secrets.
✅ Revoke once auth logs show nothing still uses it; make human access
break-glass, time-boxed, and alerted.

## Secret Management Checklist

- [ ] No credentials in source, images, CI config, or infrastructure code
- [ ] Secrets resolved at runtime from a broker (Vault, Secrets Manager, SOPS+KMS)
- [ ] Workloads authenticate by platform identity, not a bootstrap secret
- [ ] Delivered via file mount or direct API read, not environment variables
- [ ] Dynamic short-lived credentials used wherever the backend supports them
- [ ] Distinct credentials per service and per environment
- [ ] Rotation procedure uses two overlapping slots and has been executed in production
- [ ] Old credentials revoked only after audit logs confirm zero usage
- [ ] Secret-typed config wrappers prevent accidental logging
- [ ] Log and error-tracker scrubbing configured for known secret patterns
- [ ] gitleaks (or equivalent) in pre-commit *and* CI, plus platform push protection
- [ ] Every secret has a documented owner and expiry
- [ ] Access to production secrets is break-glass, time-boxed, and alerted
- [ ] Incident runbook says rotate first, clean history second
- [ ] Audit logging on secret reads, with alerting on anomalous access
