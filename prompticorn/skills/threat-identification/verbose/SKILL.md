# Threat Identification (Verbose)

## Core Patterns

### Start With Assets, Not Components

Threat identification fails when it starts from an architecture diagram, because
diagrams show components and attackers pursue assets. Build the asset register
first and rate each on confidentiality, integrity, and availability separately.

| Asset | Location | Confidentiality | Integrity | Availability |
|---|---|---|---|---|
| Deploy role (OIDC) | GitHub Actions | Catastrophic | Catastrophic | Low |
| Payment provider key | Secrets manager | Catastrophic | High | Medium |
| Customer PII | Postgres `users` | High (regulated) | Medium | Medium |
| Expense records | Postgres `expenses` | Medium | High (fraud) | High |
| Receipt images | S3 | Medium | Low | Low |
| Audit log | CloudWatch | Low | Catastrophic | Medium |

Two findings fall out of this table that a component-first pass misses. The audit
log has low confidentiality value and catastrophic integrity value — an attacker
who can edit it erases the evidence of everything else. And the deploy role
outranks the database it can reach, so hardening the database while leaving CI
credentials long-lived is inverted.

### Enumerate Every Entry Point

An entry point is any place data or control crosses from something you do not
control into something you do. The forgotten one is where the incident starts.

```
Unauthenticated network
  POST /api/login, /api/password-reset, /api/signup
  POST /webhooks/stripe          <- attacker-controlled bytes from the internet
  GET  /public/reports/:share_token
  GET  /health, /.well-known/*

Authenticated network
  43 REST routes under /api/v1
  POST /api/v1/receipts   (multipart, 10 MB, images + PDF -> image parsing libs)
  POST /api/v1/import     (CSV parsed server-side)
  GET  /admin/*           (role-gated)

Machine-to-machine
  S3 ObjectCreated -> Lambda -> OCR vendor        (egress to a third party)
  SQS consumer, 3 producers
  Nightly ETL reading a partner SFTP drop

Build and supply chain
  1,400 transitive npm deps, 200 PyPI deps
  4 base container images
  6 GitHub Actions, 2 pinned by tag rather than digest
  Anyone with write access to main

Human and operational
  Support console with "impersonate user"
  Break-glass DB access via bastion
  Laptops holding long-lived cloud keys
```

The last two blocks are the ones teams skip, and they are the highest-privilege
surfaces in the list. A build pipeline executes code from 1,600 packages. A
support console is an authentication bypass with a UI on it.

### Model Actors by Capability, Not by Adjective

"Hackers" is not an actor. An actor is defined by the access they start with,
what they can do, what they want, and whether they will persist.

| Actor | Starting access | Capability | Objective | Persists? |
|---|---|---|---|---|
| Commodity scanner | None | Automated exploitation of published CVEs | Cryptomining, ransomware | No |
| Fraudulent customer | One valid tenant account | Manual API manipulation | Inflate claims, reach other tenants | Briefly |
| Compromised laptop | An employee's live sessions | Whatever that employee can do | Depends on the operator | Yes |
| Malicious insider | Prod read, design knowledge | Legitimate tooling, knows the gaps | Bulk export, cover tracks | Yes |
| Supply-chain attacker | Publish rights on a dependency | Code execution in CI, then prod | Credential theft, backdoor | Yes |
| Funded targeted actor | None initially | Phishing, 0-day, lateral movement | Long-dwell data theft | Yes |

Two of these rows change design decisions on their own. The compromised-laptop
actor means session lifetime and step-up re-authentication matter more than
password complexity rules. The insider actor means the audit log must be
append-only and shipped somewhere the insider cannot reach.

### Trace Reachability From Asset Back to Entry Point

Threats become concrete when you can state the path. For each high-value asset,
walk backwards to every entry point that reaches it and count the hops.

```
Asset: payment provider key (secrets manager)
  <- API pod IAM role permits reading it                            (1 hop)
     <- RCE in the API container
        <- unsafe deserialization in the CSV importer               (3 hops, authenticated)
        <- vulnerable image-parsing lib in the receipt uploader     (3 hops, authenticated)
     <- SSRF in the PDF renderer reaching the metadata endpoint     (2 hops, authenticated)
  <- CI role permits reading the same secret                        (1 hop)
     <- malicious dependency executing during the build             (2 hops, UNAUTHENTICATED)

Shortest unauthenticated path: compromised npm package -> CI -> payment key.
```

That final line is the whole exercise. It says dependency pinning and scoping the
CI role matter more than anything in the request-handling path, and that no amount
of input validation shortens it. It also says the pod role should not be able to
read that secret at all.

### Write Abuse Cases Alongside User Stories

The cheapest place to identify threats is during story writing, because the person
who understands the intended behaviour is present and has not yet built anything.

```
Story: As a finance admin I can approve an expense over $5,000.

Abuse cases
  A1  A non-admin calls POST /expenses/:id/approve directly.         (authorization)
  A2  A user approves their own submission after adding
      themselves to the approver group.                             (separation of duties)
  A3  A user edits the amount after approval; the record
      still reads "approved".                                       (integrity / TOCTOU)
  A4  An approver denies ever having approved it.                   (non-repudiation)
  A5  Approval emails are used to enumerate valid
      employee addresses.                                           (information disclosure)
  A6  The bulk approval endpoint is called 10,000 times.            (DoS / cost)
```

Six threats in ten minutes from one engineer, no specialist required. Feeding them
through a STRIDE pass with trust boundaries — the threat-modeling skill — turns
them into mitigations. Running scanners and manual tests against the deployed
endpoints — the vulnerability-assessment skill — tells you which are live today.

### Keep the Output in a Register, Not a Document

Identified threats need identity so they can be tracked, disputed, and closed.

```
ID       T-014
Asset    Expense records (integrity)
Entry    POST /api/v1/expenses/:id   (authenticated, any tenant member)
Actor    Fraudulent customer
Claim    IDOR — :id is a sequential integer and the query is not tenant-scoped.
Assumes  Tenant ids are guessable (they are: sequential).
Status   Open, owner @backend, tracked as PRO-214
```

A threat with an ID gets triaged. A threat in a slide deck gets forgotten. Record
the assumption too — most closed threats reopen because an assumption changed, not
because the code did.

## Common Anti-Patterns

❌ **Starting from the architecture diagram** — you enumerate the components you
own and miss the vendor, the webhook, and the build pipeline.
✅ Start from assets, then find every path that reaches them.

❌ **"Internal only" treated as a control** — flat networks, VPN-wide access, and
SSRF each defeat it.
✅ Verify unreachability or assume the endpoint is public.

❌ **Excluding support and admin tooling from scope** — impersonation is the
highest-privilege function in most products.
✅ Model impersonation and break-glass explicitly, including who audits them.

❌ **Threats with no named actor** — "someone could tamper with the queue" cannot
be prioritized because nobody can say who or why.
✅ Every threat names an actor with the capability to execute it.

❌ **Stopping at the OWASP Top 10** — it enumerates web application flaw classes
and says nothing about insiders, supply chain, or business-logic abuse.
✅ Use it as a checklist for one category, never as the threat list.

❌ **Rating everything High** — a register with no gradient is one nobody
prioritizes from.
✅ Force a distribution using blast radius and reachability.

❌ **A one-time workshop** — the register goes stale the first time an entry point
is added.
✅ Re-run on architecture change, new integration, and new data class.

## Threat Identification Checklist

- [ ] Asset register written and ranked by C/I/A loss, not by component
- [ ] Audit log and credentials rated on integrity, not only confidentiality
- [ ] Every unauthenticated entry point enumerated, including webhooks
- [ ] Authenticated, machine-to-machine, and operational entry points listed
- [ ] Build pipeline and dependency tree treated as an entry point
- [ ] Support, admin, and impersonation tooling in scope
- [ ] Third parties and outbound data flows on the inventory
- [ ] Actors defined by starting access, capability, and objective
- [ ] Insider and supply-chain actors explicitly considered
- [ ] Reachability traced backwards from each high-value asset
- [ ] Shortest unauthenticated path to each critical asset written down
- [ ] Abuse cases written for every significant user story
- [ ] Each threat has an ID, an owner, a status, and its assumptions recorded
- [ ] Register reviewed on architecture change, not annually
