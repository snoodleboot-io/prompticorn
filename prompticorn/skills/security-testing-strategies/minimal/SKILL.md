# Security Testing Strategies (Minimal)

## Purpose
Choose and place automated security tools so each covers a class of defect the
others structurally cannot, without drowning the pipeline in false positives.

## Core Techniques

### 1. Know What Each Tool Cannot Find
| Tool | Sees | Structurally cannot find |
|---|---|---|
| SAST | Source, no execution | Anything requiring runtime state — authz logic, business rules |
| DAST | Running app, black box | Unreachable paths, anything behind auth it can't hold |
| IAST | Runtime instrumentation | Code your tests never execute |
| SCA | Dependency manifests | Bugs in *your* code |
| Secret scanning | Text patterns | Secrets that don't look like secrets |

None finds broken object-level authorization reliably. That gap is filled by
`secure-code-review` and by explicit tests, not by buying another scanner.

### 2. False-Positive Rate Decides Adoption
A scanner at 90% detection and 40% false positives gets muted within two sprints;
one at 60% detection and 5% false positives gets trusted and acted on. Tune
aggressively before you widen coverage. Measure the ratio of findings triaged to
findings fixed — if it climbs above roughly 5:1, the tool is costing more
engineering time than it returns.

### 3. Place Each Gate Where Its Latency Fits
```yaml
# pre-commit (< 5s)   secret scanning only — never let a secret reach the remote
# PR (< 5 min)        SAST on changed files, SCA on lockfile diff
# main merge (< 20m)  full SAST, container scan, IaC scan
# nightly (hours)     DAST against staging, fuzzing
```
Blocking gates belong only where the signal is near-certain: secrets, known-exploited
CVEs, and high-confidence SAST rules. Everything else reports without blocking.

### 4. Write Security Tests as Regular Tests
The highest-value security test is an ordinary test asserting a denial.
```python
def test_cannot_read_other_tenants_invoice(client, alice, bob_invoice):
    r = client.get(f"/api/invoices/{bob_invoice.id}", headers=alice.auth)
    assert r.status_code == 404      # 404 not 403 — don't confirm existence
```
Add one per endpoint. This catches the IDOR class no scanner covers, and it stays
green forever after.

### 5. Gate Dependencies on Exploitability, Not Count
```bash
pip-audit --strict            # fails on known-vulnerable Python deps
npm audit --audit-level=high  # ignore low/moderate noise in CI
trivy image --severity HIGH,CRITICAL --ignore-unfixed myapp:latest
```
`--ignore-unfixed` matters: blocking on a CVE with no available patch stops
deploys without improving security. Track it, don't gate on it.

### 6. Diff the Findings, Don't Report the Total
Report *new* findings introduced by this change against the baseline. A PR author
shown 400 pre-existing issues ignores all of them; shown the 2 their change added,
they fix both.

## Warning Signs

- A scanner in CI whose findings nobody has triaged this quarter
- The build blocked on medium-severity findings, so people rerun until green
- Suppression files growing faster than fixes
- DAST run only against a login page, so it never sees the authenticated app
- No test asserting a 403/404 for cross-tenant access on any endpoint
- Dependency scanning that gates on total CVE count rather than exploitability
- Container images scanned in the registry but never rebuilt on a new base CVE
- Security tests living in a separate suite that runs on a different cadence
