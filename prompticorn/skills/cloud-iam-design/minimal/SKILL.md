# Cloud IAM Design (Minimal)

## Purpose
Grant each identity the least authority it needs, from short-lived credentials, so that a single compromised identity cannot become a full breach.

## Core Techniques

### 1. Grant Least Privilege, Then Prove It
Start from zero and add only the specific actions on the specific resources an identity actually uses. The test is the **blast radius**: if this identity's credentials leak, what can the attacker reach? Least privilege is the practice of making that answer small.

Derive real permissions from observed usage (access logs, access analyzers) rather than guessing, and prune what has gone unused.

### 2. Prefer Roles Over Long-Lived Keys
Long-lived access keys are the most-leaked cloud secret: they end up in git, CI logs, laptops, and container images, and they stay valid until someone notices.

- Workloads on cloud compute → attach a **role** and use the instance/pod identity. No stored key.
- Humans → federate through SSO to assume short-lived roles, not static IAM users.
- CI/CD and external workloads → **workload identity federation** (OIDC trust), so the pipeline exchanges its own token for short-lived cloud credentials — no key to store or rotate.

Every static key you eliminate is a credential that can't leak.

### 3. Never Use Wildcards in Grants
`Action: "*"` or `Resource: "*"` is how "temporary" grants become permanent breaches. Wildcards silently absorb every future permission and resource the platform ever adds.

Name the actions and the resource ARNs/paths explicitly. Wildcards are acceptable only in a *deny* (denies should be broad), never in an allow you can enumerate.

### 4. Bound Authority With Permission Boundaries and SCPs
Least-privilege policies say what an identity *can* do; boundaries cap what it can *ever* do, even if someone later attaches a broader policy.

- **Permission boundaries** cap the effective permissions of a role/user.
- **Organization policies / SCPs** set guardrails across whole accounts (e.g. deny disabling logging, deny leaving approved regions).

This lets you delegate policy creation to teams without letting them grant themselves admin.

### 5. Separate by Account and Environment
Blast radius is also structural. Put prod and non-prod in **separate accounts/projects** so a compromised dev identity cannot touch production. Use distinct roles per service and per environment; avoid one shared "app" identity that every service assumes.

### 6. Keep the Human Break-Glass Path Auditable
Emergency admin access should exist, but be rare, MFA-gated, time-bound, and loudly logged. Standing human admin is the credential attackers most want.

## Warning Signs
- `Action: "*"` or `Resource: "*"` in any allow policy
- Long-lived access keys in CI, containers, or developer machines
- One shared identity/role reused across many services
- Prod and non-prod sharing an account or credentials
- Permissions never reviewed against actual usage
- No permission boundary or org guardrail — any role can be widened to admin
- Standing human administrator access with no expiry or MFA

## See Also
- `secret-management` — storing and rotating any credential that must exist
- `security-architecture-review` — evaluating blast radius across the system
