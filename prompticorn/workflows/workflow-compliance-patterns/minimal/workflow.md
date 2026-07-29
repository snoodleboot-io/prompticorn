---
name: "workflow-compliance-patterns"
description: Ensure workflows meet compliance and regulatory requirements
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Compliance Patterns Workflow

Making the workflow emit the evidence a regulation requires as a by-product of
running. `workflow-security-in-workflows` establishes the controls; this proves
they operated continuously.

## Core Concepts
- **Evidence is a run output, not an audit-time artifact.** Controls tested once a
  year prove nothing about the intervening months
- Every control gets a machine-checkable assertion whose result is retained for the
  full audit period

## Pattern Types
- **Data classification:** drives every other requirement; **propagates through
  joins** — PII joined to public data is still PII
- **Residency enforcement:** fail closed, never fail over out of region; an
  in-region step calling an out-of-region API is still a transfer
- **Retention with deletion:** obligations are two-sided (keep ≥ X, delete after Y);
  most implementations skip the delete side
- **Subject rights requests:** access/erasure as workflows with legal deadlines,
  returning data in intelligible (decrypted) form
- **Change control:** assert `approver != author` in CI, not in a policy document

## When to Use
- Any workflow handling personal, financial, or health data, or in scope for
  SOC 2 / ISO 27001 / GDPR / HIPAA / PCI-DSS

## Key Considerations
- **Deletion scope is where this fails:** backups, caches, search indices, DLQ, and
  logs all hold copies. Enumerate every one and verify absence after
- **Over-retention is itself a violation** under data-protection regimes
- Aggregation rarely anonymizes — most aggregates are re-identifiable
- Set retention from the longest applicable obligation, not the shortest
