# Security Testing Strategies (Verbose)

## Core Patterns

### Choosing Tools by What They Structurally Cannot See

Every category of tool has a blind spot that follows from its mechanism, not from
its quality. Buying a better product in the same category does not close it.

| Category | Mechanism | Strong on | Blind by construction |
|---|---|---|---|
| SAST | Parses source, no execution | Injection sinks, hardcoded secrets, unsafe APIs | Runtime state, authorization intent, config-dependent behavior |
| DAST | Fires requests at a running app | Reflected XSS, missing headers, TLS config, auth flow gaps | Code it never reaches; anything needing valid app state |
| IAST | Agent instruments the running app | Confirmed reachable injection with low false positives | Paths your test suite never executes |
| SCA | Reads lockfiles and manifests | Known CVEs in dependencies, license issues | Vulnerabilities in first-party code |
| Secret scanning | Regex plus entropy over text/history | Committed keys and tokens | Secrets not matching a known shape |
| IaC scanning | Parses Terraform/K8s/CloudFormation | Public buckets, open security groups, wildcard IAM | Drift — what is actually deployed |
| Fuzzing | Mutates inputs against a harness | Memory safety, parser crashes, panics | Logic bugs where no input crashes anything |

The union of all seven still misses broken object-level authorization, broken
business logic, and design flaws. Those belong to `secure-code-review` at the line
level and `security-architecture-review` at the design level.

### False-Positive Economics

Detection rate is the number vendors sell on. Adoption is determined by precision.

| Precision | Effect on a team |
|---|---|
| > 80% | Findings treated as real; fixed on sight |
| 50–80% | Triaged, with grumbling; survives if volume is low |
| 20–50% | Rubber-stamped suppressions; signal is lost |
| < 20% | Muted, disabled, or routed to a channel nobody reads |

Start narrow and high-precision, then expand: enabling every rule on day one
produces a backlog so large the tool never recovers credibility. Track findings
per PR and the fix-to-suppress ratio; when suppressions outpace fixes, stop
adding rules and tune.

### Pipeline Placement

Latency budget determines placement; confidence determines whether it blocks.

```yaml
# .github/workflows/security.yml
name: security
on: [pull_request, push]

jobs:
  secrets:                      # < 30s — always blocking, near-zero false positives
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }        # full history: a secret in an old commit still leaked
      - run: gitleaks detect --redact --exit-code 1

  sast:                         # < 5 min on PRs — blocking only on high-confidence rules
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: semgrep ci --config p/security-audit --config p/secrets
        env:
          SEMGREP_BASELINE_REF: origin/main   # report only what this PR introduced

  deps:                         # < 2 min — blocking on fixable high/critical
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip-audit --strict
      - run: trivy fs --severity HIGH,CRITICAL --ignore-unfixed .
```

Beyond the PR: merge to main runs full SAST, container image and license scans,
blocking on critical only. Nightly against staging runs DAST, an IAST-instrumented
E2E pass, and fuzzing — non-blocking, filing tickets. Manual pentest and
architecture review run quarterly.

`SEMGREP_BASELINE_REF` is the detail that makes SAST survivable on a legacy
codebase: the author sees the findings their diff introduced, not the thousand
that predate them.

### Security Tests as Ordinary Tests

The highest-return security testing is not a scanner. It is negative-path tests in
the normal suite, running on every PR, written by the engineer who built the feature.

```python
import pytest

def test_cross_tenant_read_is_denied(client, alice, bob_invoice):
    r = client.get(f"/api/invoices/{bob_invoice.id}", headers=alice.auth)
    assert r.status_code == 404       # 404, not 403 — 403 confirms the id exists

def test_role_escalation_via_mass_assignment_ignored(client, alice):
    client.patch("/api/me", json={"display_name": "A", "role": "admin"},
                 headers=alice.auth)
    assert alice.reload().role == "member"

def test_price_is_recomputed_server_side(client, alice, product):
    r = client.post("/api/cart", json={"sku": product.sku, "price": "0.01"},
                    headers=alice.auth)
    assert r.json()["line_total"] == str(product.price)

@pytest.mark.parametrize("url", ["http://169.254.169.254/latest/meta-data/",
                                 "http://127.0.0.1:6379/", "file:///etc/passwd"])
def test_webhook_url_rejects_internal_targets(client, alice, url):
    r = client.post("/api/webhooks", json={"url": url}, headers=alice.auth)
    assert r.status_code == 400
```

These cover exactly the classes scanners cannot reach, run in milliseconds, and
never regress once written. One per endpoint is a reasonable standard.

### Making DAST Actually Useful

A DAST run against an unauthenticated front page tests almost nothing — it needs
a session and a map of the application.

```bash
# Feed the scanner an OpenAPI spec so it enumerates real endpoints
# rather than guessing from crawled links
zap-api-scan.py \
  -t https://staging.example.com/openapi.json \
  -f openapi \
  -z "-config replacer.full_list(0).replacement=Bearer ${STAGING_TOKEN}" \
  -r zap-report.html
```

Run it against staging with seeded data, never production. Provide credentials for
each distinct role — a scanner holding only an admin token cannot detect that a
member role reaches an admin endpoint.

### Coverage Model

Map defect classes to detection methods so gaps are explicit, not assumed away.

| Defect class | Primary detection |
|---|---|
| SQL / command injection | SAST, confirmed by IAST or DAST |
| XSS | SAST for sinks, DAST for reflection |
| Vulnerable dependency | SCA on every build |
| Leaked credential | Secret scanning, pre-commit and full history |
| Misconfigured cloud resource | IaC scan plus deployed-state drift check |
| Broken object-level authz | Negative-path unit tests + human review |
| Broken business logic | Human review, pentest |
| Design / trust-boundary flaw | Architecture review |

## Common Anti-Patterns

❌ **Enabling every rule on day one** — thousands of findings, instant credibility
loss, permanent suppression file.
✅ Start with a high-precision pack, baseline existing findings, expand gradually.

❌ **Blocking the build on all severities** — teams learn to rerun and merge past it.
✅ Block on secrets and fixable critical CVEs; report everything else.

❌ **Reporting cumulative findings on a PR** — the author is not responsible for
the backlog and will ignore the whole report.
✅ Diff against a baseline ref; surface only what this change introduced.

❌ **Gating on CVE count including unfixable ones** — deploys stop and security
does not improve.
✅ `--ignore-unfixed` in the gate; track unfixable CVEs separately with an owner.

❌ **DAST against an unauthenticated page** — measures the login form only.
✅ Authenticated scans, one per role, driven from an API spec against seeded staging.

❌ **Treating a clean scan as a security sign-off** — no tool in the table finds
authorization or logic flaws.
✅ Pair automation with human review at both the code and architecture levels.

❌ **Security tests in a separate suite on a separate cadence** — they rot, then
get deleted for being flaky.
✅ Same suite, same run, same required status check as every other test.

## Security Testing Checklist

- [ ] Secret scanning at pre-commit and over full git history, blocking
- [ ] SAST on PRs, baselined so only new findings surface; tuned for precision
- [ ] SCA on every build; gate on fixable high/critical only
- [ ] IaC scanning for public exposure, wildcard IAM, unencrypted storage
- [ ] Container images scanned at build and rescanned on a schedule
- [ ] DAST authenticated, spec-driven, one pass per role, against staging
- [ ] Negative-path tests for cross-tenant access on every endpoint
- [ ] Tests for mass assignment, server-side price recomputation, SSRF targets
- [ ] Security tests in the main suite and in the required status check
- [ ] Fuzzing for any parser or handler taking untrusted binary input
- [ ] Each defect class mapped to a named detection method; gaps documented
- [ ] Blocking gates limited to near-certain signal
- [ ] Findings routed to an owning team with an SLA by severity
- [ ] Manual pentest and architecture review scheduled for what tools cannot cover
