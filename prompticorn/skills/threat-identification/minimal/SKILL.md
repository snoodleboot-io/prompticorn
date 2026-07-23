# Threat Identification (Minimal)

## Purpose
Enumerate what could go wrong in a system before deciding what to do about it — inventory the assets worth attacking, the entry points that reach them, and the actors who would try.

## Core Techniques

### 1. Inventory Assets First
You cannot enumerate threats against something you have not named. List what an attacker wants, and what the loss costs you.

| Asset | Where it lives | Loss if compromised |
|---|---|---|
| Customer PII | `users`, `addresses` tables | Regulatory exposure, breach notification |
| Session identifiers | Browser, Redis | Full account takeover |
| Payment provider key | Secrets manager, CI | Direct financial loss |
| Receipt images | S3 bucket `expense-receipts` | PII exposure, no integrity impact |
| Deploy credentials | GitHub Actions OIDC role | Total system compromise |

Rank by blast radius, not by how interesting the component is. Deploy credentials outrank the database, because they grant the database.

### 2. Enumerate Entry Points
Every place untrusted input crosses into your code is an entry point.

```
Unauthenticated: login, password reset, signup, webhook receiver, health endpoints
Authenticated:   43 REST routes, file upload, CSV import, admin console
Machine:         S3 event -> Lambda, SQS consumer, partner SFTP drop
Build:           1,400 transitive npm deps, 4 base images, 6 GitHub Actions
Operational:     bastion SSH, kubectl, support console with "impersonate user"
```

Webhooks and build pipelines are the ones teams forget. A webhook handler parses attacker-controlled bytes from the internet; a pipeline executes attacker-controlled code the moment a dependency is compromised.

### 3. Name Actors by Capability
A threat is only real if someone with matching capability wants the asset.

| Actor | Starts with | Capability | Objective |
|---|---|---|---|
| Commodity scanner | Nothing | Automated, published CVEs only | Cryptomining, ransomware |
| Fraudulent customer | One valid account | Manual API manipulation | Reach another tenant, inflate claims |
| Malicious insider | Prod read, design knowledge | Legitimate tooling | Bulk export, cover tracks |
| Supply-chain attacker | Publish rights on a dep | Code execution in CI | Credential theft, backdoor |
| Funded targeted actor | Nothing | Phishing, 0-day, persistence | Long-dwell data theft |

Defending against a funded actor when your real exposure is commodity scanning wastes budget; the reverse underspends.

### 4. Trace Reachability From Asset Back To Entry Point
For each high-value asset, walk backwards and count hops.

```
Asset: payment provider key
  <- API pod IAM role can read it                          (1 hop)
     <- RCE via the CSV importer                           (3 hops, authenticated)
     <- SSRF in the PDF renderer -> instance metadata      (2 hops, authenticated)
  <- CI role can read the same secret                      (1 hop)
     <- malicious npm dependency runs in the build         (2 hops, UNAUTHENTICATED)
```
The shortest unauthenticated path is the finding. Here it says dependency pinning and CI role scoping beat anything in the request path.

### 5. Write Abuse Cases Beside User Stories
Invert every story while the person who wrote it is still in the room.

```
Story: "As a user I can export my expense report as PDF."
Abuse: export another tenant's report by editing report_id.        (authz / IDOR)
Abuse: supply a template making the renderer fetch
       http://169.254.169.254/ and leak instance credentials.      (SSRF)
Abuse: queue 10,000 exports and exhaust the render workers.        (DoS / cost)
```

This produces the raw threat list. Structuring and mitigating it is threat modeling; proving which threats are live in the deployed system is vulnerability assessment.

## Warning Signs

- No written asset inventory — the team argues over what "critical" means
- Architecture diagrams with no third parties, webhooks, or CI on them
- Threat lists that stop at the OWASP Top 10 and never mention insiders or supply chain
- "Internal only" used as a control, with no verification the endpoint is unreachable
- Support and impersonation tooling declared out of scope because "only employees use it"
- Threats with no named actor — a sign they were invented, not identified
- Every threat rated High, so nothing is actually prioritized
- The register was produced in one workshop and has not changed since
