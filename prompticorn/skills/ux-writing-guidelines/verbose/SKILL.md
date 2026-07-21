# UX Writing Guidelines (Verbose)

## Core Patterns

### Error Messages

An error message has exactly one job: get the user unstuck. It needs three
components, and most shipped errors have none of them.

1. **What happened to their data** — is the work lost, saved, partially applied?
2. **Why, in their model of the world** — not the system's.
3. **What to do next** — one concrete action, ideally a button.

```
❌ "An error occurred."
❌ "Invalid input."
❌ "Error 422: unprocessable entity"
❌ "Request failed. Please try again later or contact support."
```

The last one is the most common and the most quietly hostile: it tells the user
nothing about whether their work survived, gives no cause, and offers an action
("contact support") that costs them twenty minutes.

```
✅ "We couldn't save your changes — the connection dropped.
    Your draft is stored on this device.
    [ Retry ]"

✅ "That card was declined by your bank. We weren't told why.
    Try another card, or contact your bank — they can usually
    clear the block immediately."

✅ "Passwords need at least 12 characters. Yours has 8."

✅ "This file is 4.2 GB. The limit is 2 GB.
    Try splitting it, or use the desktop uploader for large files."
```

Notice that none of them say "please", "sorry" more than once per flow, or
"unfortunately". Apology inflation reads as insincere and delays the useful part.
Apologise once, when it is genuinely your fault and it genuinely cost the user
something — a failed payment, lost work — and never for their own typo.

**Blame direction.** Move the subject away from the user without contorting the
sentence.

```
❌ "You entered an invalid email address."
❌ "You must select at least one option."
✅ "That doesn't look like an email address. Check for a missing @."
✅ "Pick at least one option to continue."
```

**Never surface the mechanism.** `null constraint violation on user_id`,
`ECONNREFUSED`, and `422` mean nothing to a user and quite a lot to an attacker.
Log the detail with a correlation id and show the id only where support will
actually use it: "If this keeps happening, quote reference 8F2A-31."

**Validate at the right moment.** Inline, on blur, next to the field, is where a
format error belongs — not in a summary banner after submit. Reserve the banner
for errors that are not attributable to one field ("This workspace is at its
50-member limit").

### Buttons and Action Labels

A button label must survive being read completely alone, because that is how
screen-reader users encounter it when tabbing, and roughly how skimmers do too.

```
❌ [ OK ]        ❌ [ Submit ]     ❌ [ Yes ] [ No ]     ❌ [ Confirm ]

✅ [ Delete 3 files ]              ✅ [ Send invoice ]
✅ [ Create account ]              ✅ [ Move to archive ]
```

Rules that hold up in practice:

- **Verb + object.** "Save changes" beats "Save". "Add member" beats "Add".
- **Echo the heading's verb.** A dialog titled "Discard draft?" gets "Discard
  draft", never "Confirm" or "Yes". The mismatch is what makes users hesitate.
- **Count the objects when it is destructive.** "Delete 3 files" makes a
  wrong-selection mistake visible at the last possible moment, for free.
- **The dismissive option is also a verb, not "Cancel", when the stakes are
  real.** "Keep files" is unambiguous where "Cancel" is genuinely ambiguous in a
  deletion dialog — it can be read as cancelling the files.
- **Never label a button with the state it will enter.** "Loading…" replacing
  "Save" is fine; a button that reads "Saved" and is still clickable is not.

### Confirmation Dialogs

"Are you sure?" is the canonical bad dialog. It asks the user to re-affirm a
confidence they already demonstrated by clicking, supplies no new information,
and — because it appears everywhere — is dismissed reflexively. It provides the
feeling of a safety net without the net.

```
❌  Are you sure?
    Are you sure you want to delete this item?
    [ OK ]   [ Cancel ]
```

```
✅  Delete 3 projects?
    This also deletes 47 files and 12 shared links, including 2 links
    that are currently public. This can't be undone.
    [ Delete 3 projects ]   [ Cancel ]
```

The replacement supplies what the user could not otherwise know: the blast
radius, the surprising secondary effects, and the reversibility. That is
information they can actually act on, and it is the only justification for
interrupting them.

**The better answer is usually no dialog at all.** Make the action reversible
and confirm after the fact:

```
✅  3 projects deleted.  [ Undo ]        (toast, 10 seconds, then a
                                          30-day trash for recovery)
```

Undo beats confirm on every axis: it does not interrupt the 99% of correct
actions, it actually recovers the 1%, and it does not train dismissal reflexes.
Reserve modal confirmation for actions that are genuinely irreversible and
genuinely high-cost — deleting an account, revoking production credentials,
sending to 40,000 recipients. For the very worst of those, require typing the
object's name rather than adding another "yes" button.

### Empty States

An empty state is the most-read and least-written screen in most products. The
user is present, has nothing else to look at, and does not yet know what the
feature is for. "No data" throws that away.

There are three distinct empty states and they need different copy:

```
Nothing created yet — teach:
❌ "No saved searches."
✅ "No saved searches yet.
    Save a search and we'll email you when new matches appear.
    [ Save your current search ]"

A filter matched nothing — offer the exit:
❌ "No results."
✅ "No invoices match 'overdue' in the last 30 days.
    [ Clear filters ]  or try a wider date range."

Everything is done — acknowledge and stop:
✅ "Inbox zero. Nothing needs your attention."
    (no button, no teaching, no illustration of a task)
```

Conflating the first two is the common bug: a user who filtered to nothing gets
onboarding copy telling them to create their first invoice, when they have four
hundred.

### Voice and Tone

Voice is the product's personality and never changes. Tone is the register for a
particular moment and must change with the stakes. A product with one tone
everywhere is either flippant during failures or cold during onboarding.

| Context | Tone | Example |
|---|---|---|
| Onboarding | Warm, encouraging, second person | "Let's get your first project set up — it takes about two minutes." |
| Routine success | Neutral, brief, past tense | "Invoice sent." |
| User-caused error | Plain, non-blaming, corrective | "That date is in the past. Pick today or later." |
| System-caused error | Plain, accountable, reassuring about data | "We couldn't process that. Your card wasn't charged." |
| Destructive action | Precise, flat, quantified | "This deletes 47 files. It can't be undone." |
| Payment / billing | Serious, exact, no jokes | "Your plan renews on 14 March for $240." |
| Security | Serious, specific about the action taken | "We ended your session because your password changed. Sign in again." |
| Outage / incident | Direct, honest, timed | "Search is down. We're working on it and will update by 15:00 UTC." |

The failure mode is playfulness leaking into the wrong quadrant. A witty error on
a declined payment reads as a company that does not understand it just cost you
something in front of a customer. Humour is a low-stakes device: empty states,
onboarding, 404s. Never in errors involving money, data loss, permissions, or
security.

Avoid anthropomorphising the system into helplessness — "Oops! Our hamsters fell
off the wheel!" is unusable to a user trying to determine whether their invoice
sent.

### Writing for Translation

Copy that reads well in English and translates badly is a defect that surfaces
six months later in a locale you cannot read.

```
❌  "Delete " + count + " files"          (word order differs by language)
✅  delete_files: "Delete {count, plural, one {# file} other {# files}}"

❌  "Are you sure you want to remove " + name + " from " + team + "?"
✅  remove_member_confirm: "Remove {name} from {team}?"
```

- **Never concatenate.** Build one string per message with named placeholders.
  Word order is not universal; a fragment assembled in code cannot be reordered.
- **Use a plural-aware format** (ICU or equivalent). "1 files" is a bug, and
  languages with three or six plural forms cannot be served by an if/else.
- **Give translators context in the key and a comment.** "Close" is a verb on a
  button and an adjective in "close match"; the translator sees only the string.
- **Budget for expansion.** German and Finnish commonly run 30-40% longer than
  English; short labels can double. Design buttons and nav to survive it.
- **Do not embed markup or bake in formatting.** Dates, currency, and numbers go
  through locale formatters, never a hand-written pattern.
- **Idioms and puns do not survive.** "Knock it out of the park" becomes
  meaningless or absurd. Say what you mean literally in the source string.

### Writing for Screen Readers

Screen-reader users hear elements out of visual context — a control at a time,
or a list of all links, or all headings. Copy must carry its own meaning.

```
❌ <a href="/report">Click here</a> to download the report.
✅ <a href="/report">Download the Q3 report (PDF, 2 MB)</a>

❌ <button aria-label="button">×</button>
✅ <button aria-label="Close dialog">×</button>

❌ <img alt="image">                    ❌ <img alt="chart.png">
✅ <img alt="Revenue rose from $1.2M in Q1 to $1.9M in Q3">
```

- **Link text must be unique and self-describing.** A page with nine "Learn more"
  links produces a link list of nine identical entries.
- **Icon-only controls need an accessible name** that matches what a sighted user
  would call it, so voice-control users can say it.
- **Announce state changes.** A toast that appears visually is silent unless it
  is in a live region — a save that "worked" but was never announced reads as a
  failure.
- **Alt text describes the information, not the file.** Purely decorative images
  take `alt=""` so they are skipped entirely, which is better than being read.
- **Do not rely on placeholder text as a label.** It disappears on focus and is
  inconsistently announced. Use a real, visible label.

### Terminology Consistency

Users assume different words mean different things. If the nav says "workspace",
settings says "team", and billing says "organization", a reasonable user
concludes there are three objects and goes looking for the other two.

Keep a terms table in the repo, next to the components, and treat a synonym
introduced in a PR as a review comment like any other defect.

| Use | Never | Why |
|---|---|---|
| workspace | team, org, organization, account | One container concept, one name |
| member | user, seat, person, collaborator | "Seat" is billing-internal jargon |
| sign in / sign out | log in, login, log out | "Login" is the noun only |
| delete | remove, destroy, purge, trash | Reserve "remove" for taking out of a group without deleting |
| archive | hide, deactivate | Archive is recoverable; say so |
| plan | subscription, tier, package | One billing noun |

Also fix casing conventions and stick to them. Sentence case for headings,
buttons, labels, and menu items ("Save changes", not "Save Changes") — it reads
faster, and it leaves capitals free to signal proper nouns and product names.
Numerals for all numbers including one through nine, because interfaces are
scanned rather than read. Serial comma. No exclamation marks outside genuine
celebration, and at most one per screen.

### Forms, Labels, and Helper Text

- **Labels are visible and permanent.** Placeholder-as-label fails on focus, in
  translation, and for screen readers.
- **Say what a field is for when it is not obvious** — "Display name — shown on
  your public profile" — and say nothing when it is. Helper text on "Email" is
  noise.
- **Mark optional fields, not required ones,** when most are required. The
  asterisk convention scales badly and is unpronounceable.
- **State constraints before the user hits them.** "12+ characters" under the
  password field prevents the error that "Password too short" reports.
- **Explain why you need sensitive data at the point of asking.** "Phone number —
  used only for account recovery, never for marketing" measurably lifts
  completion and is a promise you must then keep.

## Common Anti-Patterns

❌ **"An error occurred" / "Something went wrong"** — no cause, no data status,
no next action.
✅ What happened to their work, why in their terms, one thing to do next.

❌ **Exposing the mechanism** — `422`, `ECONNREFUSED`, constraint names.
✅ Human cause in the UI, detail in the log, a short reference id if support
needs one.

❌ **Blaming the user** — "You entered an invalid email address."
✅ "That doesn't look like an email address. Check for a missing @."

❌ **OK / Cancel / Submit / Yes / No buttons** — meaningless when read alone,
which is how screen readers and skimmers read them.
✅ Verb plus object, echoing the heading: "Delete 3 files" / "Keep files".

❌ **"Are you sure?"** — no new information, dismissed reflexively, provides the
feeling of safety without the fact of it.
✅ Name the consequence, quantify it, state reversibility — or replace the dialog
with an undo.

❌ **Confirmation dialogs on reversible actions** — interrupts the 99% who were
right and trains the reflex that defeats the 1% case.
✅ Act immediately, confirm with a toast and an Undo, keep a trash.

❌ **"No data" empty states** — the highest-attention screen in the product used
to say nothing.
✅ What goes here, why it is worth having, one button. Different copy for
filtered-to-nothing.

❌ **Constant tone regardless of stakes** — jokes on a declined payment.
✅ Tone tracks consequence; humour only where nothing is at risk.

❌ **Apology inflation** — "Sorry!", "Unfortunately", "We apologise for any
inconvenience" stacked in one message.
✅ One apology, only when it is your fault and it cost them something.

❌ **Concatenated strings** — "Delete " + n + " files" cannot be reordered by a
translator.
✅ One key per message with named, plural-aware placeholders.

❌ **"Click here" links and icon-only buttons with no name** — a link list of
nine identical entries; a button announced as "button".
✅ Self-describing link text and accessible names on every icon control.

❌ **Three words for one object** — workspace / team / organization across nav,
settings, and billing.
✅ A terms table in the repo; synonyms caught in review.

❌ **Title Case and sentence case on the same screen** — reads as two products
stitched together.
✅ Sentence case everywhere, enforced in review.

❌ **Placeholder text as the label** — vanishes on focus, unreliable for
assistive tech, untranslatable in context.
✅ A visible, persistent label plus separate helper text where warranted.

## UX Writing Checklist

- [ ] Every error states what happened to the user's data
- [ ] Every error gives a cause in the user's terms, not the system's
- [ ] Every error offers one concrete next action, or says none is needed
- [ ] No HTTP codes, stack traces, or constraint names in user-facing text
- [ ] No copy blames the user for an input mistake
- [ ] Format errors validate inline, next to the field, not in a submit banner
- [ ] Every button is verb + object and readable in isolation
- [ ] Button verb matches the heading's verb
- [ ] Destructive buttons state the count of affected objects
- [ ] No dialog asks "Are you sure?"
- [ ] Confirmations state blast radius, secondary effects, and reversibility
- [ ] Reversible actions use undo rather than a confirmation dialog
- [ ] Irreversible, high-cost actions require typing the object's name
- [ ] Empty states teach, and filtered-empty states offer to clear the filter
- [ ] Tone matches stakes; no humour in money, data-loss, or security copy
- [ ] At most one apology per flow, and only where it's warranted
- [ ] No string built by concatenation; one key per message
- [ ] Plurals use a plural-aware format, not if/else on n == 1
- [ ] Translator comments present on ambiguous strings
- [ ] Layout survives 40% text expansion
- [ ] Dates, numbers, and currency go through locale formatters
- [ ] Link text is unique and self-describing; no "click here"
- [ ] Icon-only controls have accessible names matching their visible concept
- [ ] Status changes announced in a live region, not visually only
- [ ] Alt text describes information; decorative images use empty alt
- [ ] Every form field has a visible, persistent label
- [ ] Constraints stated before submission, not only in the error
- [ ] Sensitive fields explain why the data is needed
- [ ] Terminology checked against the terms table
- [ ] Sentence case used consistently across headings, buttons, and labels
