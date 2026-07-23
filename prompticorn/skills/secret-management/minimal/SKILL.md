# Secret Management (Minimal)

## Purpose
Keep application credentials — database passwords, API tokens, webhook signing keys — out of source, out of logs, and short-lived enough that a leak has a deadline.

## Core Techniques

### 1. Fetch Secrets at Runtime, Never Bake Them In
```python
# ❌ In source, in the image, in the Helm values file
DB_PASSWORD = "hunter2"

# ✅ Resolved at startup from a broker the workload authenticates to
import boto3, json
secret = json.loads(
    boto3.client("secretsmanager").get_secret_value(SecretId="prod/db")["SecretString"]
)
```
The workload's identity (IAM role, Kubernetes ServiceAccount, Vault auth) is what unlocks the secret. That identity is issued by the platform and is not copyable into a laptop.

### 2. Prefer Files or Direct API Reads Over Environment Variables
Env vars leak in ways that are easy to miss:
- `/proc/<pid>/environ` — readable by any process of the same user, and by sidecars sharing a PID namespace
- Crash dumps and APM error reports frequently serialize the whole environment
- `docker inspect` and Kubernetes pod specs show them in plaintext
- Child processes inherit them, so a subprocess call hands your DB password to a shell script

A mounted `tmpfs` file with mode `0400` is meaningfully harder to exfiltrate accidentally. If env vars are unavoidable, keep them to low-value config, not credentials.

### 3. Use Short-Lived Dynamic Credentials Where the Backend Supports It
```bash
vault read database/creds/orders-api    # returns a new DB user, TTL 1h, auto-revoked
```
A one-hour credential turns "we leaked a password" into "we leaked something that expired before the pager went off". This is the single largest reduction in credential risk available.

### 4. Make Rotation a Two-Secret Operation
Rotation breaks when there is one credential and one moment of change. Instead: create the new credential, make consumers accept both, cut writers over, then revoke the old.

| Credential | Rotation | Notes |
|---|---|---|
| Dynamic DB creds | Continuous (TTL) | No rotation event at all |
| Static DB password | 90 days | Use two accounts, alternate them |
| Third-party API key | 90 days | Most vendors allow two live keys — use both |
| Webhook signing secret | 180 days | Verify against old and new during overlap |

### 5. Redact at the Logging Boundary
```python
class Settings(BaseModel):
    db_password: SecretStr        # repr() renders as '**********'
```
Do not rely on developers remembering. Use a type that cannot be printed, and add a log filter that scrubs known secret patterns (`AKIA[0-9A-Z]{16}`, `ghp_`, `sk-`, `-----BEGIN`).

### 6. Block Secrets at Commit Time
```bash
gitleaks protect --staged --redact     # pre-commit hook
gitleaks detect --log-opts="--all"     # full history scan
```
Also enable the platform's push protection (GitHub secret scanning). Detection after the fact is far more expensive than prevention.

### 7. Treat Any Committed Secret as Compromised
`git rebase`, `filter-repo`, and force-push do not undo exposure. Forks, clones, CI caches, and mirrors keep the object. **Rotate the credential first**, then clean history if you care to.

## Warning Signs

- `.env`, `credentials.json`, or `*.pem` tracked in git — or in `.dockerignore` but not `.gitignore`
- Secrets in Kubernetes manifests, Helm values, or Terraform `.tfvars` committed to the repo
- Base64-encoded Kubernetes `Secret` treated as encryption (it is encoding, nothing more)
- The same credential used by every service and every environment
- No expiry on API tokens; credentials older than the engineers who created them
- Secrets passed as CLI arguments — visible in `ps aux` and shell history
- Secrets appearing in stack traces, request logs, or error-tracker payloads
- A secret leak "fixed" by rewriting git history without rotating the credential
- Developers with standing read access to production secrets
