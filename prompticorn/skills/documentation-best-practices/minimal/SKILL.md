# Documentation Best Practices (Minimal)

## Purpose
Separate the four kinds of documentation, generate everything that can rot, and
delete the pages nobody reads.

## Core Techniques

### 1. Four Kinds, Never Mixed
Most bad documentation is not badly written — it is two kinds welded together.
The Diátaxis distinction: what the reader is doing splits along *learning vs
working*, and *practical vs theoretical*.

| Kind | Reader is | Written as | Test |
|---|---|---|---|
| **Tutorial** | Learning, new | A guaranteed-to-work lesson | A beginner finishes with a working thing |
| **How-to** | Working, competent | Steps for one real goal | Solves a task someone actually has |
| **Reference** | Working, looking something up | Dry, complete, structured | Answers "what are the arguments" in 10s |
| **Explanation** | Learning, curious | Prose about why | Answers "why is it like this" |

```
Tutorial:     "Build your first pipeline" — one path, our sample data,
              every command given, no choices offered, works verbatim.
How-to:       "Retry a failed pipeline run" — assumes you have a
              pipeline; five steps; no teaching.
Reference:    `Pipeline.run(inputs, *, timeout=300, retries=3)` — every
              parameter, type, default, and raised exception.
Explanation:  "Why pipelines are immutable" — the concurrency problem
              that forced it, and what we gave up.
```

The classic failure: a "Getting started" page that stops mid-tutorial to explain
the architecture, then lists every config option. The learner loses the thread,
the looker-up cannot find the table. Split it into three pages and both work.

### 2. Docs as Code
Docs live in the repo, in the same PR as the change, reviewed by the same
reviewer. Docs in a separate wiki drift within one quarter — nothing forces them
to move when the code does. Make the doc a required part of the change for
anything that alters an interface or an operational procedure.

### 3. Generate or Test Everything That Can Rot
Hand-written docs decay at the rate the code changes. So do not hand-write the
parts that track code:

- **API reference** — generate from docstrings/OpenAPI/type signatures. A
  hand-maintained parameter table is wrong within two releases.
- **Code samples** — put them in the test suite (doctest, or extract-and-run in
  CI). An untested sample is a sample that will not run.
- **CLI help, config options, env vars** — generate from the definitions.
- **Links** — a link checker in CI catches the 404s nobody reports.

What is left is what humans should be writing: the how-to, the why, and the
first-five-minutes path.

### 4. A README That Works
In order, and stop there:

1. **One sentence** on what this is and who it is for.
2. **Why you'd use it** — 2-3 lines, or the problem it solves.
3. **Install** — one block, copy-pasteable.
4. **Smallest useful example** — real code, real output shown.
5. **Links out** — full docs, how-tos, contributing, licence.

Not in the README: architecture essays, every config flag, the changelog, a
feature matrix. Those are separate pages, linked. A README that scrolls for
three screens before showing code is a README that fails its one job.

### 5. Write the First Five Minutes Deliberately
Take an install-to-first-success path and time it on someone who has never seen
the project. Every prerequisite you assumed, every "obviously you'd set the API
key", every command that fails on a clean machine — that is your highest-value
fix list. This path must work verbatim on a fresh environment, be re-run in CI,
and offer no choices. Choices belong in how-tos; the first five minutes gets one
opinionated path to a working result.

### 6. Know When Not to Write Docs
A page explaining that `process(data, True, False)` means "validate but don't
retry" is documentation of a design defect. Fix the signature to
`process(data, validate=True, retry=False)` and the page becomes unnecessary.
Before writing, ask whether a rename, a better default, a clearer error message,
or a deleted option would remove the need. Docs that exist to compensate for a
confusing interface must be maintained forever and are read by roughly half the
people who hit the confusion.

## Warning Signs

- One page tries to teach, instruct, and enumerate at once
- The getting-started guide does not work on a clean machine
- Parameter tables hand-maintained next to a generator that could emit them
- Code samples nothing executes — and that no longer compile
- Docs in a wiki, changed in a different PR from the code, or not at all
- "See the code for details" in reference documentation
- A README where the first code block is below the fold
- Pages last edited two years ago with no owner and no review date
- Documentation written to explain around a confusing API
- Screenshots of UI that changed three releases ago
