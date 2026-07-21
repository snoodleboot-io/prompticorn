# Product Analytics Setup (Verbose)

## Core Patterns

### The Event Taxonomy

An analytics implementation degrades along a predictable path: it starts clean,
each team adds events in their own style, and within a year nobody can answer a
question without first asking three people what an event means. The taxonomy is
what prevents that, and it only works if it is enforced in code review.

**Convention: `object_action`, past tense, snake_case, singular object.**

| Event | Why it's shaped that way |
|---|---|
| `project_created` | Object first, so all project events sort together |
| `project_archived` | Same object, obvious sibling |
| `invoice_paid` | Past tense: the event records something that happened |
| `checkout_started` | Names a state change, not a button |
| `teammate_invited` | Domain vocabulary, matches how the team speaks |

Rejected forms, and the specific damage each does:

| Anti-form | Damage |
|---|---|
| `Clicked Checkout Button` | Dies at the next redesign; casing invites `clicked checkout button` |
| `payment` | Cannot distinguish attempted / authorised / settled / refunded |
| `user_did_signup` | Verb-first breaks sorting; `did` adds nothing |
| `project_create` | Present tense reads as a command, not a record |
| `signup_completed_new_flow` | Variant encoded in the name instead of a property |
| `page_view` with 40 property shapes | One event that means everything means nothing |

Two structural rules matter more than the naming style:

1. **Events are state changes, not interactions.** Track `project_created`, not
   `clicked_new_project`. The state change is stable across every redesign; the
   click is not. Interaction events belong in a separate, explicitly disposable
   namespace (`ui_*`) that nobody builds a metric on.
2. **Properties carry the dimensions; events carry the fact.** Resist making a new
   event for each variant. `signup_completed` with `signup_channel` beats
   `signup_completed_google` / `_github` / `_email`, which cannot be summed
   without someone remembering all three exist.

Standard properties on every event, set once in a wrapper rather than by each
caller:

```
event            string   canonical name from the tracking plan
occurred_at      ts       UTC, event time (not ingest time)
event_version    int      bumped when meaning changes
user_id          string   null when anonymous
anonymous_id     string   always present
account_id       string   the billing/workspace entity
source           enum     server | web | ios | android
app_version      string   for client sources
schema_version   int      envelope version, separate from event_version
```

Carrying both `occurred_at` and the ingest timestamp is what lets you distinguish
"users stopped doing this" from "the pipeline was 6 hours behind".

### The Tracking Plan

The tracking plan is the contract. It lives in version control next to the code —
not in a spreadsheet someone owns — and PRs that add events without updating it
do not merge.

| Event | Fires when | Source | Required properties | Owner | Ver |
|---|---|---|---|---|---|
| `signup_completed` | Account row committed | Server | `signup_channel`, `plan`, `referrer_domain` | Growth | 1 |
| `project_created` | POST /projects → 201 | Server | `project_id`, `template_id`, `is_first_project` | Core | 2 |
| `teammate_invited` | Invite row committed | Server | `invite_id`, `role`, `invite_method` | Core | 1 |
| `invite_accepted` | Invitee's account linked | Server | `invite_id`, `days_since_invite` | Core | 1 |
| `checkout_started` | Checkout session created | Server | `cart_value_cents`, `currency`, `item_count` | Billing | 2 |
| `invoice_paid` | Processor webhook `settled` | Server | `invoice_id`, `amount_cents`, `currency`, `processor` | Billing | 1 |
| `subscription_cancelled` | Cancel committed | Server | `reason_code`, `mrr_cents`, `tenure_days` | Billing | 1 |
| `search_performed` | Results painted | Web/iOS | `query_length`, `result_count`, `latency_ms` | Search | 1 |
| `export_failed` | Export job errors | Server | `export_format`, `error_code`, `row_count` | Core | 1 |

Property typing conventions that prevent most downstream grief:

- **Money**: integer minor units (`amount_cents`) plus explicit `currency`. Floats
  accumulate rounding error and an implied currency breaks the moment you sell
  outside your home market.
- **Durations**: integer milliseconds with the unit in the name (`latency_ms`).
- **Booleans**: prefixed `is_` / `has_`, never a string `"true"`.
- **Enums**: closed sets, documented in the plan. `reason_code` with 6 known
  values is analysable; a free-text reason is not.
- **Never** put raw search queries, emails, names, or tokens in properties.
  `query_length` and `result_count` answer the analytical question without
  turning the warehouse into a PII store subject to deletion requests.

Enforce the plan in CI: a schema registry, or a generated typed client so that
`track("projet_created")` fails to compile rather than producing a silent ghost
event that nobody notices for four months.

### Versioning Events

The single most damaging analytics operation is quietly changing what an event
means. It is damaging precisely because nothing errors — the charts keep drawing,
with a step change that gets attributed to product work.

```
Before: checkout_started fires on cart page view
After:  checkout_started fires when the payment form loads

Effect: checkout_started volume drops 38% overnight.
        checkout_started -> invoice_paid conversion jumps 22% -> 36%.
Both changes are definitional. Neither is a product improvement.
```

The migration that works:

1. Emit `checkout_started_v2` (or same name with `event_version: 2`) alongside v1.
2. Run both for 2-4 weeks. Measure the offset explicitly and record it.
3. Migrate dashboards and metric specs to v2, annotating the changeover date.
4. Announce a deprecation date for v1; stop emitting it on that date.
5. Keep both definitions in the tracking plan, v1 marked deprecated with its dates.

A version bump is required whenever the trigger point moves, the population that
fires it changes, a required property is removed or its meaning narrows, or the
unit of a numeric property changes. Adding an optional property is not a version
bump. The parallel discipline for metric definitions is in
`success-metrics-definition`.

### Identity Resolution

Most analytics questions span the anonymous/identified boundary — "which channel
produces users who retain?" needs pre-signup and post-signup behavior stitched to
one person. That stitching is a deliberate mechanism, not something the SDK does
for free.

```
1. First visit
   anonymous_id = "a3f9c2..."   (1st-party cookie + localStorage, 13-month TTL)
   page_viewed, pricing_viewed, docs_viewed  -> anonymous_id only

2. Signup
   identify(user_id="8821", anonymous_id="a3f9c2...")
   -> writes an alias row: (anonymous_id a3f9c2...) => (user_id 8821)

3. Thereafter
   events carry user_id AND anonymous_id while the cookie survives

4. Backfill
   the alias lets you re-attribute step-1 events to user 8821
```

Three identifier layers, kept distinct because B2B analysis needs all three:

| Identifier | Scope | Used for |
|---|---|---|
| `anonymous_id` | Device + browser profile | Pre-signup attribution |
| `user_id` | A person | Individual engagement, seat activity |
| `account_id` | Workspace / billing entity | Retention, revenue, churn — almost all reporting |

Reporting "user retention" in a B2B product where an account has 40 seats mostly
measures seat churn, not customer churn. Get the grain right first.

Where identity resolution legitimately fails, and how to bound it:

| Case | Effect | Mitigation |
|---|---|---|
| Incognito / cleared cookies | New `anonymous_id`; pre-signup trail lost | Accept; measure the share of signups with no prior anonymous events |
| Cross-device (mobile → desktop) | Two anonymous trails, one user | Alias both to the `user_id` when each device authenticates |
| Shared device | Two users on one `anonymous_id` | Reset `anonymous_id` on logout |
| ITP / 7-day cookie caps | Returning visitors look new | 1st-party server-set cookies; expect inflated "new visitor" counts |

Never merge identities on email hashes or fingerprints as a workaround. It is a
privacy exposure, it is often wrong, and merges are effectively irreversible.

### Client-Side Undercounting and Server-Side Truth

Client-side events are lossy by nature. Typical loss is 10-30%, and the drivers
are systematic rather than random:

| Cause | Typical loss | Notes |
|---|---|---|
| Ad/tracker blockers | 8-25% | Developer and privacy-conscious audiences at the top of that band |
| Browser tracking prevention | 2-8% | Safari/Firefox defaults; also truncates cookie lifetime |
| Page unload before flush | 1-5% | Mitigate with `sendBeacon`, never a synchronous XHR |
| Network failure / offline | 1-3% | Higher on mobile networks |
| Corporate proxies and CSP | 1-5% | Enterprise segments specifically |

The critical property is that the loss is *biased*: the blocked users skew
technical, privacy-aware, desktop, and enterprise. So client-side data does not
just undercount, it misrepresents segment mix. Any conclusion of the form "our
users are mostly consumer/mobile" drawn from client data alone is suspect.

The split that works:

| Emit server-side | Emit client-side |
|---|---|
| Signup, activation milestones | Scroll depth, hover, rage clicks |
| All revenue and billing events | Client render latency, TTI |
| Subscription lifecycle | Form field abandonment |
| Permission and admin changes | Client-side error surfacing |
| Anything feeding a forecast or invoice | Anything only the browser can observe |

Server-side events should be emitted inside the transaction that commits the state
change — or from an outbox drained after commit — so the event and the row cannot
disagree. Firing on request receipt rather than commit produces events for
requests that later rolled back.

Where both sides track the same action, monitor the ratio as an operational
signal:

```
client_checkout_started / server_checkout_started
  steady-state 0.78 (measured over 8 weeks)
  alert if the 7-day mean moves outside 0.68 - 0.88
```

That drop from 0.78 to 0.41 is a broken script tag or a new CSP rule, and without
this ratio it surfaces as a mysterious "conversion improvement" — the denominator
shrank, as described in `success-metrics-definition`.

### Funnels, and Finding the Real Drop-Off

A funnel is not meaningful until you have fixed four things: the ordered step
list, the conversion window, whether steps must be strictly ordered, and the
identifier grain.

```
Funnel: self-serve signup -> first payment
Grain:  account_id      Window: 14 days from signup_completed
Order:  strict          Counting: first occurrence per account

  signup_completed    12,410   100%     —
  project_created      8,190    66%    -4,220
  teammate_invited     3,760    46%    -4,430
  invoice_paid           890    24%    -2,870
```

Percentages mislead here. Step 2→3 shows the biggest *absolute* loss (4,430) even
though its percentage drop is smaller than step 1→2's. Prioritise absolute
volume, since that is what recovery is worth.

But do not act before segmenting. The aggregate almost always hides the finding:

| Segment | signup→project | Note |
|---|---|---|
| Desktop, Chrome | 78% | Baseline |
| Desktop, Safari | 74% | Fine |
| Mobile web, iOS | 41% | The actual bug |
| Mobile web, Android | 44% | Same bug |
| Invited by teammate | 89% | Social proof works |
| Paid search | 52% | Intent quality, not a bug |

The aggregate said "onboarding needs work". The segmentation says the project
creation flow is broken on mobile web, which is a two-day fix rather than a
quarter of onboarding redesign.

Two further checks before believing any funnel: confirm the step events did not
change version inside the analysis period, and confirm the final cohort has had
the full 14-day window. A partial trailing cohort makes every funnel look like it
is degrading.

## Common Anti-Patterns

❌ **Tracking clicks instead of state changes** — `clicked_signup_button` dies at
the next redesign and never matched actual signups anyway.
✅ Track `signup_completed` at the point the account row commits.

❌ **Redefining an event in place** — history becomes uninterpretable and the step
change is misread as a product effect.
✅ Version the event, dual-emit, annotate the changeover, deprecate on a date.

❌ **Revenue from client-side events** — 10-30% undercount, biased by segment, and
it will not reconcile with finance.
✅ Server-side emission from the committing transaction, reconciled to billing.

❌ **Money as a float, currency implied** — rounding drift plus a silent
multi-currency bug the day you sell abroad.
✅ Integer minor units plus an explicit `currency` on every monetary event.

❌ **A new event per variant** (`signup_completed_google`, `_github`) — nobody
remembers the full set, so every total is quietly wrong.
✅ One event, a `signup_channel` property.

❌ **No alias on signup** — the acquisition trail is severed and channel
attribution becomes guesswork.
✅ `identify()` linking `anonymous_id` to `user_id` at signup and at every login.

❌ **Reporting user-grain retention for a B2B product** — measures seat movement,
not customer churn.
✅ Fix the grain to `account_id` for retention and revenue.

❌ **PII in event properties** — raw queries, emails, names create a deletion
obligation across the whole warehouse.
✅ Derived properties only: `query_length`, `result_count`, `domain_category`.

❌ **Funnels without a window or a stated denominator** — the number changes
depending on who runs it.
✅ Window, grain, ordering, and counting rule stated with the funnel.

❌ **A tracking plan in a spreadsheet, drifting from the code** — within two
quarters it documents a product that no longer exists.
✅ Plan in version control, enforced by a schema registry or generated client.

## Product Analytics Checklist

- [ ] Naming convention documented (`object_action`, past tense, snake_case)
- [ ] Events model state changes; interaction events isolated in a `ui_*` namespace
- [ ] Tracking plan in version control, updated in the same PR as the code
- [ ] Every event has a named owner and a trigger described precisely
- [ ] Standard envelope on every event: ids, source, timestamps, versions
- [ ] Both event time and ingest time recorded
- [ ] Money as integer minor units with explicit currency
- [ ] Durations carry units in the property name
- [ ] Enum properties are closed sets documented in the plan
- [ ] No PII in event properties; derived attributes only
- [ ] Event versioning policy defined, with dual-emit and deprecation dates
- [ ] `anonymous_id` set first-party and persisted; alias emitted at signup/login
- [ ] `user_id` and `account_id` tracked separately; reporting grain agreed
- [ ] `anonymous_id` reset on logout
- [ ] All financial and contractual events emitted server-side, post-commit
- [ ] Client/server ratio monitored with an alert threshold
- [ ] Schema validation in CI; unknown or malformed events rejected loudly
- [ ] Funnels specify window, grain, ordering, and counting rule
- [ ] Funnel analysis segmented before any conclusion is drawn
- [ ] Immature trailing cohorts excluded from funnel and retention reporting
- [ ] Deletion path exists to honour data subject requests across the warehouse
