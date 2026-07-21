# Incident Response Planning (Verbose)

## Core Patterns

### Severity Levels That Mean Something

A severity level is a commitment about response — who wakes up, how fast, and
who is told. Write the definitions so that a tired engineer can classify in
under a minute, using customer impact rather than technical cause.

| Sev | Definition | Concrete examples | Response commitment |
|---|---|---|---|
| SEV1 | A core business function is unavailable, or data is lost or exposed | Checkout returns errors for all users; primary database unrecoverable; customer records readable by the wrong tenant | Page immediately, any hour. IC assigned. All-hands allowed. Leadership notified within minutes. Public status page updated. |
| SEV2 | Major degradation with a workaround, or a large subset affected | Search latency 20x; one region down with traffic shifted; async jobs delayed hours | Page immediately, any hour. IC assigned. Status page if externally visible. |
| SEV3 | Limited impact, no urgency | An internal report is broken; one non-critical queue growing slowly; a single tenant's minor feature | Ticket, business hours. No page. |
| SEV4 | No customer impact; hygiene | Redundant node lost with capacity intact; a flapping alert; an expiring certificate with weeks left | Ticket, normal planning. |

Two rules keep this honest. First, name data loss and security exposure inside
SEV1 explicitly — they are not "degradation", and teams routinely under-rate
them because the service is still up. Second, when two levels seem to fit, take
the higher one and downgrade later; the cost is asymmetric.

Add response-time expectations by severity so "immediately" is measurable — for
example acknowledge within 5 minutes at SEV1 and 15 at SEV2 — and then track
whether you actually meet them.

### Incident Command

Roles exist so that no one person holds an unbounded job. Assign them out loud
and record who holds each.

**Incident Commander.** Owns the incident, not the fix. The IC holds the current
picture, assigns work by name, makes the call between competing mitigations,
decides severity, decides when to escalate, and decides when the incident is
over. The IC's tools are questions: what do we know, what are we trying, what
would tell us we are wrong, who is doing it.

**Operations lead / responders.** The people with hands on the system. They
report findings up to the IC and take direction; they do not unilaterally
restart production because they had an idea.

**Communications lead.** Owns the status page, customer-facing updates, and
internal stakeholder traffic. Their most valuable function is absorbing the
"any update?" messages that would otherwise interrupt whoever is debugging.

**Scribe.** Timestamps events, decisions, and metric changes as they happen.
This makes the postmortem cheap and accurate — see `incident-timeline-creation`
for the structure. Reconstructing an hour of Slack a week later loses most of it.

The IC must not debug. Once the IC is inside a query, nobody is tracking the
whole picture, updates slip, two responders start conflicting mitigations, and
the escalation clock stops. Small teams may combine IC and comms, or IC and
scribe. Never combine IC and hands-on-keyboard.

Hand off command explicitly and out loud: "I am handing IC to Priya. Priya, you
have IC." Ambiguous command is worse than no command. On long incidents, plan
handoffs at fixed intervals rather than waiting for exhaustion.

### Declaring an Incident

The dominant failure in practice is not over-reacting — it is a single engineer
investigating alone for 45 minutes, hoping it resolves, before telling anyone.
Every minute there is undetected impact with no IC, no comms, and no help.

Design against it:

- **Anyone can declare, at any severity, with no approval.** A junior engineer
  declaring a SEV2 that turns out to be a SEV4 did the right thing.
- **Declaring is one action.** A slash command, one button — not a form.
- **Downgrading and closing are routine and blameless.** Publish the numbers:
  if you never downgrade anything, you are declaring too late.
- **Bias rules.** Write down the cases where you always declare: any customer
  data exposure, any suspected security event, any total loss of a core flow,
  any time you are unsure whether it is customer-impacting.

Also define what is *not* an incident, so the process is not diluted: planned
maintenance running long but within window, single-user issues with a known
workaround, and known-degraded dependencies already tracked.

### Escalation and Paging Policy

Escalation should be automatic, time-based, and written down, because a tired
responder is the worst possible judge of whether they need help.

```
Time-based (automatic, enforced by the paging tool):
  Primary on-call            page → ack expected within 5 min
  No ack after 5 min         → page secondary on-call
  No ack after 10 min        → page the engineering manager on duty
  No ack after 15 min        → page the duty director

Trigger-based (the IC's standing instructions, not a judgement call):
  SEV1 declared              → notify leadership immediately
  30 min at SEV1, unmitigated→ page the service owner and widen the call
  Any suspected data exposure→ page security on-call and legal contact
  Any customer-visible SEV1  → comms lead posts within 15 min of declaration
  Third-party root cause     → open the vendor's severity-1 channel now
```

Paging policy needs to state the contract in both directions: what on-call owes
(acknowledge in N minutes, be reachable, have laptop and access) and what the
organisation owes (a working runbook per alert, no daytime meetings expected
during a night shift, time off after a rough night, and a real secondary).

Check the mechanics regularly. Access that expired, a paging integration that
silently stopped delivering, a rotation that points at someone who left — these
are discovered during outages far more often than they should be.

### Communications Cadence

Commit to intervals by severity and hold them even when the update is "no
change". Silence is read as abandonment, and it generates exactly the inbound
traffic that slows the responders down.

| Severity | External update | Internal update |
|---|---|---|
| SEV1 | Every 30 min | Every 15 min |
| SEV2 | Every 60 min if externally visible | Every 30 min |
| SEV3 | On resolution | Daily |

Templates keep the comms lead from composing under stress.

```
[INVESTIGATING] 14:05 UTC
Some customers are unable to complete checkout. We are investigating.
Next update by 14:35 UTC.

[IDENTIFIED] 14:35 UTC
The cause has been identified in a recent change to our payment service.
A rollback is in progress. Checkout remains unavailable for most customers.
Next update by 15:05 UTC.

[MONITORING] 14:58 UTC
The rollback is complete and checkout is succeeding. We are monitoring
to confirm full recovery. Next update by 15:30 UTC.

[RESOLVED] 15:30 UTC
Checkout was unavailable between 13:52 and 14:58 UTC. The cause was a
change to our payment service, which has been rolled back. We are
completing a review and will publish our findings.
```

Rules for the wording: lead with customer impact, always name the time of the
next update, never speculate on cause before you know it, never blame a vendor
or a person, and do not commit to an ETA you cannot back. "We are investigating"
is better than a guess you will retract.

Internal updates can carry more detail — current hypothesis, what has been ruled
out, what help is needed — but keep them in one channel and one thread so a
person joining at minute 40 can catch up by scrolling, not by asking.

### On-Call Health

The rotation is the substrate every incident runs on. Measure it:

| Signal | Healthy | Action if not |
|---|---|---|
| People in rotation | 6+ | Fewer means no real recovery between shifts |
| Out-of-hours pages per week | ≤ 2 | Above this, fix alerting before adding people |
| Actionable page rate | > 80% | Low means alerts are noise; responders will start ignoring them |
| Pages with a runbook | ~100% | Write the runbook or delete the alert |
| Repeat pages, same cause | 0 | The follow-up action was never done |

The most damaging pattern is the chronically noisy alert: it trains the team to
acknowledge without looking, and one night it will be real. An alert that has
paged five times without anyone acting on it is not an alert, it is a metric —
move it to a dashboard.

Exercise the plan on purpose. Game days and unannounced drills reveal the boring
failures — the runbook that references a deleted dashboard, the person without
production access, the paging rotation pointing at a former employee — that
otherwise surface only during a real SEV1.

## Common Anti-Patterns

❌ **Severity defined by component.** "Database issues are SEV1" pages people
for a degraded replica and under-rates a silent data corruption.
✅ Define severity by customer impact and data risk.

❌ **The IC is also debugging.** Command collapses the moment they open a
terminal.
✅ IC coordinates and delegates; someone else types.

❌ **Waiting for a manager to authorise declaring.** The delay is pure impact.
✅ Anyone declares, any time, no approval, downgrade freely.

❌ **Escalation left to the responder's judgement.** The person least able to
assess it is the one deep in the problem at 3am.
✅ Automatic time-based escalation plus written trigger rules.

❌ **Going quiet during the hard part.** That is exactly when stakeholders start
DMing responders individually.
✅ Post on cadence even with no news; always state the next update time.

❌ **Speculating about cause publicly.** Retractions cost far more trust than
saying "we are investigating".
✅ Publish impact and actions; publish cause when it is confirmed.

❌ **No named comms owner.** Responders end up writing status updates instead of
mitigating.
✅ Assign comms at declaration, always.

❌ **Alerts without runbooks.** A page with no documented first step wastes the
first ten minutes every time.
✅ Every paging alert links a runbook with a first action and an escalation.

❌ **Treating the plan as a document rather than a practice.** Untested plans
fail on their mechanics, not their content.
✅ Drill quarterly; fix what the drill breaks.

❌ **Closing the incident when the symptom clears.** Follow-ups evaporate.
✅ Resolution requires an owner, a review, and tracked action items.

## Incident Response Checklist

- [ ] Severity levels defined by customer impact, with concrete examples
- [ ] Data loss and security exposure named explicitly at the top severity
- [ ] Response commitment (page/ack/notify) written per severity
- [ ] IC, comms, ops, and scribe roles defined; IC does not debug
- [ ] Declaring is a single action available to anyone
- [ ] "Always declare" trigger list written down
- [ ] Automatic time-based paging escalation configured and tested
- [ ] Trigger-based escalation rules written for the IC
- [ ] Security and legal contacts reachable out of hours
- [ ] Communications cadence set per severity, with templates ready
- [ ] Status page ownership and access confirmed
- [ ] Command handoff procedure defined for long incidents
- [ ] Scribe captures timestamps live for the timeline
- [ ] Resolution criteria defined — not just "the graph looks better"
- [ ] Every paging alert has a linked runbook
- [ ] On-call rotation ≥ 6 people; page volume and actionability tracked
- [ ] Follow-up actions have owners and due dates and are reviewed
- [ ] Plan exercised in a drill within the last quarter
