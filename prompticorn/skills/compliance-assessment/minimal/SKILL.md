# Compliance Assessment (Minimal)

## Purpose
Measure honestly where your systems stand against a framework's control intent, so remediation is planned from evidence rather than discovered during an audit.

## Core Techniques

### 1. Draw the System Boundary First
Scope decides everything downstream — cost, timeline, and how much of your estate an auditor examines. Write down, explicitly, which products, environments, data stores, networks, third parties, and staff are in scope, and what is excluded and why.

Shrinking scope legitimately is the highest-leverage move available: isolate regulated data into a smaller segment, tokenize card data so most systems never touch it, or push a workload onto a provider that carries the control itself. Shrinking scope *dishonestly* — excluding a system that genuinely processes the data — is the failure that unravels an audit.

### 2. Know What Each Framework Is Actually Asking
At control level, not marketing level:

| Framework | Nature | Core question |
|---|---|---|
| SOC 2 | Attestation by an auditor against trust services criteria | Did your stated controls operate effectively over a period? |
| ISO 27001 | Certification of a management system | Do you run a risk-driven ISMS with an applicability statement and ongoing review? |
| GDPR | Regulation (EU/UK personal data) | Is there a lawful basis, minimisation, subject rights, and breach notification? |
| HIPAA | US health information | Are administrative, physical, and technical safeguards in place, with business associate agreements? |
| PCI DSS | Card brand requirement | Is cardholder data segmented, encrypted, access-controlled, monitored, and tested? |

Two structural points matter more than the details. SOC 2 Type 2 and ISO 27001 test operation *over a period*, so evidence must be continuous, not a snapshot. And GDPR and HIPAA are law — engineering practice supports compliance, it does not determine it. Involve counsel for interpretation.

### 3. Assess Control by Control, in Four Columns
For each control: what is required, what exists today, the gap, and the owner with a date.

```
Control intent: Access to production is granted on approval and reviewed periodically.
Current state:  SSO with MFA for all production access. Grants via ticket.
                No periodic review; three accounts belong to leavers.
Gap:            No recurring access review; no automated deprovisioning.
Risk:           High — leaver retains production access.
Owner / due:    Platform lead, 2026-09-30
Evidence today: SSO config export, ticket history
Evidence needed: Quarterly review records with reviewer and outcome
```

Grade honestly on a scale you define — not implemented, partially implemented, implemented but unevidenced, implemented and evidenced. "Implemented but unevidenced" is the most common real state and the one that fails audits.

### 4. Collect Evidence an Auditor Will Accept
Auditors accept evidence that is dated, attributable, complete, and reproducible. Strong evidence: system-generated configuration exports, access-review records showing reviewer and decision, ticket histories, signed policies with acknowledgement records, log samples over the full period, and change records tied to approvals.

Weak evidence: an undated screenshot, a claim in a spreadsheet, a policy nobody has acknowledged, or a control that demonstrably started working the week before fieldwork. For period-based audits, expect sampling — the auditor picks items from across the window, so a control that ran for one month of twelve will be found.

### 5. Map Controls Once, Satisfy Many Frameworks
Most frameworks demand the same underlying behaviours in different vocabulary: access control, encryption, logging, change management, vendor risk, incident response, backup and recovery, awareness training. Maintain one internal control set, and map each internal control to the frameworks it serves. Do the engineering once; produce the evidence once; present it in whatever language each framework uses.

### 6. Keep a Risk Register, Not Just a Gap List
A gap list says what is missing; a risk register says what you decided about it. Each entry: the risk, affected assets, likelihood and impact, the treatment (mitigate, transfer, avoid, accept), the owner, and the date of review. Accepted risks need a named accepter with the authority to accept them. Risk-driven decision-making is itself a control in management-system frameworks — the register is evidence.

### 7. Plan Readiness and Certification as Separate Phases
Readiness is your work: gap assessment, remediation, running the controls long enough to produce evidence. Certification is the external process. For period-based reports and certifications, the observation window is the constraint — controls must have been operating throughout, so a point-in-time report first is often the pragmatic path while you accumulate history.

## Warning Signs

- Scope drawn to be convenient rather than to match where the data flows
- Self-assessment marked compliant with no evidence attached
- Evidence created retroactively in the weeks before fieldwork
- Controls that exist as policy documents with no operating record
- Each framework pursued separately, duplicating the same work
- A risk register with accepted risks and no named accepter
- Gaps with no owner and no date
- Assuming a cloud provider's certification covers your side of it
