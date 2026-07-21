# Product Analytics Setup (Minimal)

## Purpose
Instrument a product so the numbers survive contact with a real question —
consistent names, stable definitions, and a source of truth you can bill against.

## Core Techniques

### 1. Name Events object_action, Past Tense, snake_case
Pick one convention and enforce it in code review. `object_action` sorts related
events together and stays readable at 300 events.

| Good | Bad | Why the bad one hurts |
|---|---|---|
| `project_created` | `Created Project` | Casing/spacing drift; three variants within a month |
| `invoice_paid` | `payment` | Ambiguous: attempted, authorised, settled? |
| `checkout_started` | `clicked_checkout_button` | Ties the event to a UI element that will be redesigned |
| `teammate_invited` | `user_invite_sent_v2_new` | Version and status smuggled into the name |

Rules: past tense (the event already happened), lowercase snake_case, no UI
element names, no spaces, singular object. Never track "user clicked X" — track
the state change that mattered, so the event survives the redesign.

### 2. Keep a Tracking Plan and Treat It as the Schema
The plan is the contract between product, engineering, and analysis.

| Event | Trigger | Source | Key properties | Owner |
|---|---|---|---|---|
| `signup_completed` | Account row committed | Server | `plan`, `signup_channel`, `referrer_domain` | Growth |
| `project_created` | POST /projects returns 201 | Server | `project_id`, `template_id`, `is_first_project` | Core |
| `checkout_started` | Checkout session opened | Server | `cart_value_cents`, `currency`, `item_count` | Billing |
| `invoice_paid` | Processor webhook settled | Server | `invoice_id`, `amount_cents`, `currency`, `processor` | Billing |
| `search_performed` | Results rendered | Client | `query_length`, `result_count`, `latency_ms` | Search |

Properties carry the analysis. `project_created` without `is_first_project`
cannot answer the only question anyone asks of it. Money is always integer minor
units plus an explicit `currency` — never a float, never an implied currency.

### 3. Version Events; Never Redefine One in Place
If `checkout_started` fires on cart-view today and on payment-page tomorrow, every
historical funnel silently changes meaning and the step drop looks like a product
regression. Instead emit `checkout_started_v2`, run both for 2-4 weeks, measure
the offset, then deprecate v1 on a dated schedule. Same discipline applies to
tightening a property's meaning — that is a new version too.

### 4. Resolve Identity Anonymous → Signed-In
Assign an `anonymous_id` on first touch and persist it. On signup or login, emit
an alias linking `anonymous_id` to `user_id`, then send `user_id` from then on.

```
visit    -> anonymous_id = a3f9...  (cookie/localStorage, 1st-party)
browse   -> events carry anonymous_id
signup   -> identify(user_id=8821, anonymous_id=a3f9...)
after    -> events carry user_id (and anonymous_id while available)
```

Without the alias, every acquisition source is lost at the signup boundary and
attribution reports become fiction. Expect breakage anyway: incognito, a new
device, and cookie expiry all mint a fresh `anonymous_id`. Also separate `user_id`
from `account_id` — B2B analysis is nearly always per-account.

### 5. Server-Side Is the Source of Truth for Anything Financial
Client-side events undercount by roughly 10-30% depending on audience, driven by
ad blockers, tracking-prevention defaults, page-unload before the beacon flushes,
network failures, and offline sessions. Technical audiences sit at the high end.

That loss is tolerable for UI curiosity and unacceptable for revenue, funnels
that feed forecasts, or anything an invoice depends on. Emit anything financial
or contractual from the server, ideally from the same transaction that writes the
row. Client-side is for what only the client knows: scroll depth, hover, rage
clicks, client render latency. When both exist, reconcile them and expect the
gap — a client/server ratio of 0.75 is normal, and a sudden move to 0.4 is an
outage in your tracking, not a change in user behavior.

### 6. Define Funnel Steps as Events, With a Window
A funnel is only meaningful with an ordered step list, a conversion window, and a
stated denominator.

```
signup_completed   12,410  100%
project_created     8,190   66%   -34%  <- largest drop
teammate_invited    3,760   46%   -20%
invoice_paid          890   24%   -22%
window: 14 days from signup_completed; same account_id; first occurrence only
```

Read the *absolute* loss, not the percentage: 4,220 accounts vanish before
creating a project — more than every later step combined. Segment before
concluding: if that step is 78% on desktop and 41% on mobile, the problem is a
mobile bug, not onboarding copy.

## Warning Signs

- Two events meaning the same thing with different names
- Event names containing button labels or UI positions
- Money tracked as a float or with no currency property
- Revenue numbers sourced from client-side events
- An event's meaning changed without a version bump
- No alias call, so signup severs the acquisition trail
- Funnels quoted without a conversion window or denominator
- A tracking plan that has drifted from what the code actually emits
