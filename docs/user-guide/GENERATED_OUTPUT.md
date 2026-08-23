# Generated Output Is Disposable

Everything `prompticorn` writes into your repository — `.claude/`, `.cursor/`,
`AGENTS.md`, `CLAUDE.md`, and every other tool directory — is **generated**. It
is compiled from source content plus your `.prompticorn.yaml`, and it can be
deleted and rebuilt at any time without losing anything.

That is not a caveat. It is the design, and the rest of this page is what it
buys you and what it asks of you in return.

---

## The one rule

**Never hand-edit a generated file.**

An edit made in `.claude/agents/code-agent.md` is lost the next time anyone runs
a build, and until then it is invisible to everyone reading the source it was
supposed to come from. There is no mechanism that carries it forward, and none
is planned — the whole point of generating these files is that the source is the
only place a change has to be made.

If you want different output, change the input:

| You want to change | Change this |
|---|---|
| Which agents, languages, or personas appear | `.prompticorn/.prompticorn.yaml` |
| Which tool the files are generated for | `prompticorn switch <tool>` |
| The content of an agent, skill, or workflow | The authored source it is built from |

Then rebuild.

---

## Recovering a tree someone edited

`prompticorn regenerate` is the answer to any hand-patch, any stray file, and
any tree that has been half-deleted. It throws the generated directories away
and rebuilds them from the lock:

```bash
prompticorn regenerate
```

It works from whatever state the tree is in:

| The tree | What `regenerate` does |
|---|---|
| A file was edited by hand | Overwrites it with the generated content |
| A rogue file was added | Deletes it — a rebuild alone would leave it, because nothing overwrites a file no builder writes |
| A file was deleted | Writes it back |
| The whole directory was deleted | Rebuilds it |

Afterwards the tree is byte-for-byte what the lock describes, and
`prompticorn verify` exits 0.

### It refuses when the sources moved

`regenerate` reproduces what the lock already recorded. It does **not**
re-resolve, and it never writes the lock. If your manifest or your source
content has changed since the lock was written, it stops before touching
anything:

```
Refusing to regenerate: the sources no longer match the lock, so rebuilding
would produce a tree the lock does not describe.
```

That is the right answer: a rebuild from moved sources would produce a tree
nobody asked for, and doing it after deleting the old one would leave no way
back. Run `prompticorn build` instead — that re-resolves and updates the lock —
and then commit both the new lock and the new output.

---

## Checking a tree without changing it

`prompticorn verify` is the read-only counterpart, and the one to put in CI:

```bash
prompticorn verify
```

It answers three questions, and reports every finding rather than stopping at
the first:

1. Does every output the lock names still exist, unmodified?
2. Is there anything in the generated directories the lock does not know about?
3. Does the lock carry a digest for every unit it references?

Question 2 is the one that makes this worth running. A check that only walked
the lock's own list would pass a tree with an extra agent dropped into
`.claude/agents/` — the file is not in the lock, so nothing looks at it, so
nothing complains.

Exit codes, which CI scripts can branch on:

| Code | Meaning |
|---|---|
| `0` | Clean: outputs match the lock and nothing extra exists |
| `1` | Outputs are missing, or files exist that the lock does not know about |
| `3` | The lock is unusable — corrupt, or written by a newer `prompticorn` |
| `4` | A generated file was modified by hand |

`2` is never returned. It belongs to `click`, which uses it for usage errors,
and a supply-chain signal that also fires on a mistyped flag is one people learn
to ignore.

---

## Should generated output be committed?

Both choices work, and the lock makes either one safe.

**Commit it** if your team wants the generated configuration visible in review,
or if contributors should get a working setup without installing `prompticorn`.
Commit `.prompticorn/prompticorn.lock` alongside it, and add `prompticorn
verify` to CI so a hand-edit cannot land.

**Ignore it** if you would rather keep the repository to authored content.
Commit `.prompticorn/.prompticorn.yaml` and `.prompticorn/prompticorn.lock`, add
the generated directories to `.gitignore`, and have each developer run
`prompticorn regenerate` after checkout.

Either way the lock is the thing that must be committed. It is what makes the
output reproducible rather than merely regenerable.

---

## What "reproducible" actually promises

A tree locked on one machine rebuilds to **the same bytes** on any other,
including across operating systems. That is asserted on every pull request by a
CI job that locks on Linux and then regenerates on Linux, macOS and Windows,
comparing raw bytes.

Three properties hold it up:

- **Nothing in the emit path reads the clock.** No generated file carries a
  build timestamp, so a tree locked yesterday still verifies today. `CLAUDE.md`
  carried a `Last Updated` line until this was fixed; because it used local
  time, two machines in different timezones disagreed at the same instant.
- **Every write uses LF line endings**, on every platform. Python would
  otherwise emit CRLF on Windows, which hashes identically once read back and so
  hides from every check except a byte comparison.
- **Every enumeration that affects output is sorted**, so filesystem ordering
  cannot change what gets written or in what order.

If you find output that differs between two machines, that is a defect in
`prompticorn` rather than in your project — please report it.

---

## Related

- [CLI_REFERENCE.md](./CLI_REFERENCE.md) — every command, in full
- [PROJECT_SETTINGS.md](./PROJECT_SETTINGS.md) — what lives in `.prompticorn.yaml`
