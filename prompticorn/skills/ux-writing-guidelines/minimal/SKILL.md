# UX Writing Guidelines (Minimal)

## Purpose
Write interface copy that tells the user what happened and what to do next, in
the fewest words that still leave no decision unexplained.

## Core Techniques

### 1. Errors: What Happened, Why, What To Do Next

```
❌ "An error occurred."
❌ "Invalid input."
❌ "Error 422: unprocessable entity"

✅ "We couldn't save your changes — the connection dropped.
    Your draft is stored locally. Retry"
✅ "That card was declined by your bank. Try another card, or
    contact your bank about the block."
✅ "Passwords need at least 12 characters. Yours has 8."
```

Three parts, always: the state of the user's data, the cause in their terms, and
one action they can take from here. Never blame the user ("you entered an
invalid email") and never expose the mechanism ("null constraint violation").
If there is no action, say so explicitly — "Nothing was lost; try again in a few
minutes" beats leaving them wondering.

### 2. Buttons Name Their Action, Not Their Assent

```
❌ [ OK ]  [ Cancel ]         ❌ [ Submit ]      ❌ [ Yes ] [ No ]

✅ [ Delete 3 files ]  [ Keep files ]
✅ [ Send invoice ]           ✅ [ Create account ]
```

A button label should make sense read alone, with the dialog covered. The test:
if a screen reader announces only "button, OK", does the user know what happens?
Match the verb to the heading's verb — a dialog titled "Discard draft?" gets
"Discard draft", not "Confirm".

### 3. Replace "Are You Sure?" With the Consequence

```
❌ Are you sure?
   Are you sure you want to delete this?
   [ OK ]  [ Cancel ]

✅ Delete 3 projects?
   This also deletes 47 files and 12 shared links. It can't be undone.
   [ Delete 3 projects ]  [ Cancel ]
```

"Are you sure?" asks the user to confirm their confidence, which they already
had — that is why they clicked. State what will actually happen, how much of it,
and whether it is reversible. Better still: make it reversible and skip the
dialog entirely. "3 projects deleted. Undo" interrupts nobody and is safer,
because confirmation dialogs are clicked through reflexively.

### 4. Empty States Teach the Next Action

```
❌ "No items to display."

✅ "No saved searches yet.
    Save a search to get an email when new matches appear.
    [ Save your current search ]"
```

An empty state is prime instructional space — the user is there and has nothing
else to read. Say what goes here, why it is worth having, and give one button.
Distinguish the three empty states: nothing created yet (teach), a filter
matched nothing (offer to clear the filter), and everything is done (celebrate
briefly, do not teach).

### 5. Tone Shifts With Stakes; Voice Does Not
Voice is who you are — consistent everywhere. Tone is how you sound right now.

| Context | Tone | Example |
|---|---|---|
| Onboarding | Warm, encouraging | "Let's get your first project set up." |
| Routine confirmation | Neutral, brief | "Invoice sent." |
| Error the user caused | Plain, non-blaming | "That date is in the past. Pick today or later." |
| Error we caused | Plain, accountable | "We couldn't process that. Your card wasn't charged." |
| Destructive action | Precise, flat | "This deletes 47 files. It can't be undone." |
| Payment or security | Serious, exact | "Your session ended for security. Sign in again." |

Playfulness in a failed-payment message reads as a company that doesn't
understand it just cost you something. Humour is a low-stakes-only device.

### 6. Sentence Case and One Word Per Concept
Sentence case everywhere ("Save changes", not "Save Changes") — faster to read
and lets proper nouns stand out. Then pick one word per concept and never vary
for elegance. If it is a "workspace" in the nav it is not a "team" in settings
and an "organization" in billing; users assume three different things exist.
Keep a terms table in the repo next to the components and treat a synonym in a
PR as a review comment.

## Warning Signs

- "An error occurred", "Something went wrong", "Invalid input"
- Any button labelled OK, Submit, Yes, No, or Confirm
- A dialog that asks "Are you sure?" instead of naming the consequence
- Error text that shows an HTTP code or a database constraint name
- Empty states that say "No data" and offer no next step
- Copy blaming the user: "you failed to", "you entered an invalid"
- Three words for the same object across nav, settings, and billing
- Title Case headings mixed with sentence case ones on the same screen
- Jokes in payment, permission, data-loss, or security copy
- Strings assembled from concatenated fragments in code
- Buttons that only make sense while reading the sentence above them
