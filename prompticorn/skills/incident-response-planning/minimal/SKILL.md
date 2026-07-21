# Incident Response Planning (Minimal)

## Purpose
Decide before the outage who does what, how severity is judged, and when to escalate — so response is a procedure to execute rather than a decision to argue about at 3am.

## Core Techniques

### 1. Define Severity by Impact, Not by Cause
Severity is a promise about response, so write it in terms a paged engineer can apply in thirty seconds.

| Sev | Meaning | Example | Response |
|---|---|---|---|
| SEV1 | Core function unavailable or data at risk | Checkout down; customer data exposed | Page immediately, 24/7, IC required, exec notified |
| SEV2 | Major degradation, workaround exists | Search 20x slower; one region failing over | Page immediately, 24/7, IC required |
| SEV3 | Limited or non-urgent impact | One report broken; a queue backing up slowly | Business hours, ticket, no page |
| SEV4 | No customer impact | Redundant node lost; noisy alert | Ticket, next sprint |

Include a data-loss and a security-exposure clause in SEV1 explicitly; those are not "degradation" but they are the highest severity.

### 2. Separate Command from Debugging
- **Incident Commander (IC)** — owns state, not the fix. Decides, delegates, keeps the log, calls severity, decides when to escalate and when to stop.
- **Operations / subject-matter leads** — the ones actually touching the system.
- **Communications lead** — customer-facing updates, status page, internal stakeholders. Shields the responders from the "any update?" traffic.
- **Scribe** — timestamps every action and decision (feeds `incident-timeline-creation`).

The IC must not debug. The moment the IC is head-down in a query, nobody is tracking the whole incident, nobody is timing the updates, and two responders start conflicting mitigations. On a small team one person can hold IC plus comms — never IC plus hands-on-keyboard.

### 3. Declare Early, Downgrade Freely
Under-declaring is the standard failure mode: an hour is lost while one engineer quietly hopes it resolves. Make declaration cheap and non-punitive — anyone may declare, at any severity, without permission. Downgrading a SEV1 to a SEV3 after ten minutes costs almost nothing; discovering at minute 60 that you should have paged at minute 5 costs the whole incident.

### 4. Make Escalation a Path, Not a Judgement Call
Write the ladder down with times attached: primary on-call has N minutes to acknowledge before secondary is paged, secondary N more before the engineering manager. Add trigger-based escalation too — "no mitigation after 30 minutes at SEV1, page the service owner" — so escalation does not depend on a tired responder deciding they need help.

### 5. Set a Communications Cadence and Keep It
Commit to an interval by severity (for example every 30 minutes at SEV1, hourly at SEV2) and post on time even when there is no news; silence reads as "nobody is working on it".

```
[INVESTIGATING] 14:05 UTC — Checkout is failing for some customers.
We are investigating. Next update by 14:35 UTC.

[IDENTIFIED] 14:35 UTC — Cause identified in a payment service change.
A rollback is in progress. Next update by 15:05 UTC.

[RESOLVED] 15:02 UTC — Checkout was unavailable 13:52–14:58 UTC.
The change has been rolled back and error rates are normal.
A post-incident review will follow.
```

State impact, what you are doing, and the time of the next update. No cause speculation, no blame, no jargon, no promises about timing you cannot keep.

### 6. Keep the Rotation Survivable
An on-call rotation that burns people out silently degrades every future incident. Track pages per shift, out-of-hours pages, and the share of pages that were actionable. Fewer than six people in a rotation, or a routine night that pages more than once, is a staffing or alerting problem — fix the alert quality before adding humans.

## Warning Signs

- Severity defined by which component broke rather than customer impact
- The IC is also the person running the queries
- People hesitate to declare because declaring is treated as an admission
- Escalation depends on someone deciding to ask for help
- Status updates go quiet for an hour mid-incident
- The same alert pages every week and is always ignored
- No named comms owner, so responders answer stakeholder DMs
- The plan has never been exercised outside a real outage
