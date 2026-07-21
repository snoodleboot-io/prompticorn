# Compliance Assessment (Verbose)

## Core Patterns

### Scoping and the System Boundary

Scope is the first and most consequential decision in an assessment. It
determines which systems an auditor examines, how much evidence you must
produce, and how long remediation takes. Get it wrong in either direction and
the assessment fails: too narrow and it collapses when the auditor traces a data
flow you excluded; too broad and you spend a year evidencing systems that never
touch regulated data.

Define the boundary by following the data, not the org chart:

| Question | What it establishes |
|---|---|
| What regulated data exists, and of what kind? | Which framework applies at all |
| Where does it enter the estate? | Ingress systems in scope |
| Where is it stored, processed, transmitted? | The core in-scope set |
| What can reach those systems? | Connected systems, often forgotten |
| Which third parties receive or hold it? | Vendor and subprocessor scope |
| Who administers those systems? | People, access paths, workstations |
| What supports them? | Identity, logging, CI/CD, backups — usually in scope |

The commonly missed categories are the supporting ones: the identity provider,
the CI/CD system that can deploy to production, the log aggregator holding
regulated data in its indexes, backups and their restoration path, and
administrator laptops.

Reducing scope legitimately is the highest-leverage engineering work available,
and it is done by architecture rather than by argument:

- **Segment** so regulated data lives in a smaller, controlled environment with
  enforced network and identity boundaries.
- **Tokenize or vault** sensitive values so downstream systems handle a
  reference rather than the data — this is how card scope is usually shrunk.
- **Minimise** by not collecting or not retaining what you do not need. Data you
  never hold needs no controls.
- **Transfer** by using a provider that operates the control, then evidencing
  your oversight of that provider rather than the control itself.

Whatever you exclude, document why, and be able to demonstrate the exclusion
technically. "That system does not process the data" must be provable with
network and access evidence, not asserted.

### What the Frameworks Actually Require

Work at the level of control intent. Do not cite clause numbers you have not
verified against the current text of the standard, and do not treat any of this
as legal advice — for GDPR and HIPAA in particular, interpretation belongs to
counsel and your engineering work supports their determination.

**SOC 2** is an attestation report produced by a licensed audit firm against the
trust services criteria — security always, plus availability, confidentiality,
processing integrity, or privacy if you choose them. You define your controls;
the auditor tests whether they were designed appropriately and, in a Type 2
report, whether they operated effectively across an observation period. The
implication for engineering: continuous operating evidence over the whole
period, not a snapshot.

**ISO 27001** certifies an information security management system. The emphasis
is on the system of management — scope definition, risk assessment methodology,
a statement of applicability recording which controls apply and why any are
excluded, defined objectives, internal audit, and management review — with the
control set applied on the basis of assessed risk. Certification involves a
staged external audit and ongoing surveillance, so the ISMS must be seen to be
running, not assembled for the visit.

**GDPR** governs personal data of people in the EU and UK. The engineering-facing
obligations centre on: a lawful basis for each processing purpose, data
minimisation and storage limitation, transparency, mechanisms to satisfy data
subject rights (access, deletion, portability, objection) within statutory
deadlines, security appropriate to the risk, records of processing, controls on
international transfers, contracts with processors, and breach notification
within tight timeframes. Concretely, this means you need a data inventory, the
ability to find and delete one person's data across every store and backup, and
a breach process that can meet a deadline measured in hours.

**HIPAA** applies to protected health information held by covered entities and
their business associates. It requires administrative, physical, and technical
safeguards — risk analysis, workforce access management, audit controls,
integrity protection, transmission security — plus business associate agreements
with anyone handling the data on your behalf, and a defined breach notification
process.

**PCI DSS** is imposed contractually by the card brands on anyone handling
cardholder data. It is the most prescriptive of the five: network segmentation
of the cardholder data environment, no storage of sensitive authentication data
after authorisation, encryption in transit and at rest, strict access control on
a need-to-know basis, logging and log review, vulnerability management with
scanning, penetration testing, and secure development practices. Validation
effort depends on transaction volume and how you handle the data — outsourcing
the payment page to a compliant provider dramatically reduces what applies.

### Running the Gap Assessment

The assessment is a structured comparison of required state against actual
state. Run it as a data-gathering exercise, not an opinion survey.

1. **Build the control list.** Start from your internal control set (see
   mapping, below) and the framework's requirements. One row per control.
2. **Interview the owner and inspect the system.** Ask how it works, then verify
   independently. Configuration exports and logs beat descriptions; people
   sincerely describe the process as designed rather than as practised.
3. **Grade against a defined scale.** Use four states, because the middle two
   are where reality lives:

   | Grade | Meaning |
   |---|---|
   | Not implemented | The control does not exist |
   | Partially implemented | Exists for some systems, or some of the time |
   | Implemented, not evidenced | It works; you cannot prove it operated |
   | Implemented and evidenced | It works and produces retained, dated records |

4. **Record the gap with an owner and a date.** A gap without both is a note,
   not a plan.
5. **Rate the risk** so remediation can be sequenced by exposure rather than by
   ease.

```
Control intent : Production access is granted on documented approval,
                 limited to least privilege, and reviewed periodically.
Applies to     : SOC 2 (logical access), ISO 27001 (access control),
                 PCI DSS (need-to-know access), HIPAA (workforce access)
Owner          : Platform lead
Current state  : SSO with MFA enforced for all production access. Grants
                 raised as tickets with manager approval. No recurring
                 review. Sample of 40 accounts found 3 belonging to leavers
                 and 6 with privileges beyond their role.
Grade          : Partially implemented
Gap            : No periodic access review; offboarding does not revoke
                 production roles; no least-privilege verification.
Risk           : High — former employees retain production access
Remediation    : (a) automate deprovisioning from the HR system,
                 (b) quarterly access review with recorded reviewer and
                     decision, (c) reduce standing privilege to on-demand
Due            : 2026-09-30
Evidence today : SSO configuration export, access-grant ticket history
Evidence needed: Four quarters of review records with reviewer, date,
                 decision, and resulting changes
```

Sample rather than assert. Pull forty access grants, twenty changes, ten
onboardings and offboardings, and check them. An auditor will, and it is far
better to find the exceptions yourself.

### Evidence That Auditors Accept

Evidence has to show the control operated — for period-based assessments,
throughout the period, not on the day someone remembered.

| Strong | Weak |
|---|---|
| System-generated exports with timestamps | Undated screenshots |
| Access review records naming reviewer, date, decision, action taken | "We review access regularly" |
| Change records linked to approvals, tests, and deployments | A description of the change process |
| Log samples spanning the full observation period | Logs from the last two weeks |
| Signed policies with per-person acknowledgement records | A policy PDF on a shared drive |
| Ticket histories showing the workflow as designed | A workflow diagram |
| Scan and penetration test reports with remediation tracked | A scan report with no follow-up |
| Vendor assessments and executed agreements | A vendor's marketing page |

Four properties make evidence hold up: it is **dated**, **attributable** to a
person or system, **complete** across the period, and **reproducible** — you can
generate it again on request and get consistent results.

Expect sampling. The auditor selects items from across the window; a control
that began operating two months before fieldwork will be visible in the gaps.
This is the reason the annual scramble fails, and the reason to move toward
continuous collection — see `compliance-automation`.

### Mapping Controls Across Frameworks

Frameworks overlap heavily in substance and diverge in vocabulary. Maintain a
single internal control set and map outward, so engineering happens once.

```
IC-07  Privileged access is time-bound, approved, logged, and reviewed
       ├─ SOC 2       logical access criteria
       ├─ ISO 27001   access control / privileged access management
       ├─ PCI DSS     need-to-know restriction and unique IDs
       ├─ HIPAA       workforce access management safeguards
       └─ GDPR        security appropriate to risk (Art. 32 obligations)
       Owner    : Platform lead
       Evidence : IdP export, JIT grant log, quarterly review records
       Tested   : continuously (automated) + quarterly (manual review)
```

Common controls that carry across nearly everything: access control and
authentication, encryption in transit and at rest, centralised logging and
monitoring, change management, vulnerability and patch management, backup and
tested restoration, incident response, vendor risk management, security
awareness training, asset inventory, and secure development practices.

The mapping is also the answer to a second framework arriving. Adding ISO 27001
after SOC 2 is largely a documentation and management-system exercise if the
underlying controls are already mapped and evidenced.

### Risk Register

Frameworks built around management systems expect risk-driven decisions, and
the register is how you evidence that. Each entry needs the risk, the assets
affected, likelihood and impact using a scale you have defined, the existing
controls, the treatment decision, an owner, and a review date.

The treatment options are mitigate, transfer, avoid, and accept. Acceptance is
legitimate and often correct — but it requires a named individual with the
authority to accept, a documented rationale, and a review date. An accepted risk
with no accepter is an unmanaged risk wearing a label.

Keep the register live. Feed it from incidents, penetration tests, vulnerability
scans, vendor assessments, and architecture reviews. A register whose entries
all date from the same afternoon tells an auditor exactly what happened.

For threat identification, use `threat-modeling`; for technical findings that
feed the register, use `vulnerability-assessment`; for the infrastructure
controls themselves, `iac-best-practices`.

### Readiness Versus Certification

Two distinct phases, and conflating them causes most schedule surprises.

**Readiness** is internal: scope, gap assessment, remediation, and then a
sustained period of the controls actually running while evidence accumulates.
Remediation is usually the visible work, but the accumulation period is the
binding constraint — a control implemented today cannot demonstrate twelve
months of operation.

**Certification or attestation** is the external phase: selecting an assessor,
the audit itself, responding to findings, and receiving the report or
certificate. It has its own lead times, and assessor availability is a real
scheduling constraint.

The practical consequence: if a customer needs a report soon, a point-in-time
assessment first while you build operating history is usually the honest path.
Committing to a period-based report before the controls have been running is how
teams end up manufacturing evidence, which is the one failure that cannot be
remediated.

## Common Anti-Patterns

❌ **Scoping for convenience.** Excluding a system because evidencing it is hard
collapses when the auditor traces the data flow.
✅ Scope by where regulated data actually goes; reduce scope by architecture.

❌ **Self-assessing as compliant with nothing attached.** A spreadsheet full of
green cells is not an assessment.
✅ Every "implemented" carries the evidence that proves it.

❌ **Manufacturing evidence before fieldwork.** Sampling across the period finds
it, and it converts a finding into a credibility problem.
✅ Start collecting when the control starts operating.

❌ **Confusing a written policy with an operating control.** The policy is the
intent; the records are the control.
✅ Grade "implemented but unevidenced" honestly and fix the record-keeping.

❌ **Running each framework as a separate project.** The same control gets
implemented and evidenced three times.
✅ One internal control set, mapped outward to every framework.

❌ **Assuming the cloud provider's certification covers you.** It covers their
side of the shared responsibility model.
✅ Know which controls you inherit and evidence the rest yourself.

❌ **A risk register nobody revisits.** Entries all created on one day, none
reviewed since.
✅ Live register fed by incidents, tests, and reviews, with review dates.

❌ **Accepting risks anonymously.** "The business accepted it" names no one.
✅ Named accepter with authority, rationale, and a review date.

❌ **Gaps with no owner or date.** They persist to the next assessment
unchanged.
✅ Every gap has one accountable owner and a committed date.

❌ **Treating engineering judgement as legal interpretation.** Regulatory
obligations are not an implementation detail.
✅ Engineers evidence and implement; counsel interprets.

## Compliance Assessment Checklist

- [ ] Regulated data types inventoried, with where each is stored and processed
- [ ] System boundary documented, including connected and supporting systems
- [ ] Exclusions documented with a technical justification you can demonstrate
- [ ] Scope reduction opportunities evaluated (segmentation, tokenization, minimisation)
- [ ] Applicable frameworks identified with the obligations that follow
- [ ] Internal control set defined and mapped to each framework
- [ ] Every control has a named owner
- [ ] Each control graded on a defined scale, with evidence cited
- [ ] Sampling performed rather than relying on described process
- [ ] Gaps recorded with risk rating, remediation, owner, and due date
- [ ] Evidence dated, attributable, complete for the period, reproducible
- [ ] Evidence retention period defined and met
- [ ] Risk register live, with treatment decisions and named accepters
- [ ] Vendor and subprocessor inventory with assessments and agreements
- [ ] Shared responsibility boundary understood for each provider
- [ ] Incident response and breach notification paths tested
- [ ] Data subject / individual rights request process demonstrably works
- [ ] Observation period planned so evidence exists before fieldwork
- [ ] Readiness and certification phases scheduled separately
- [ ] Continuous evidence collection planned to replace the annual scramble
