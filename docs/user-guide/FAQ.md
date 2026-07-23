# Frequently Asked Questions

This FAQ is organized by who you are and what you are trying to do. Jump to the
section that fits you best. For deeper walkthroughs, see the sibling docs linked
throughout: [../QUICKSTART.md](../QUICKSTART.md),
[../TROUBLESHOOTING.md](../TROUBLESHOOTING.md), [TOOLS.md](TOOLS.md), and
[../../CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## New user / evaluator

**What is prompticorn?**
prompticorn turns one shared prompt library into ready-to-use configuration for
16 different AI coding assistants. The library holds 26 primary agents, roughly
100 workflows, 96 skills, and 26 language convention sets. Instead of hand-writing
per-tool config, you generate it from a single source of truth.

**Which AI coding assistants are supported?**
Sixteen tools today: Kilo (CLI and IDE), Claude, Cline, Cursor, GitHub Copilot,
Copilot Chat, Roo Code, Junie, Zed, Gemini CLI, Amazon Q, Windsurf, Continue,
Aider, and Codex. See [TOOLS.md](TOOLS.md) for the per-tool details.

**How do I get started?**
Run `prompticorn init`. It is interactive and walks you through choosing your
tool and what to include, then writes the config files into your repository. The
full first-run walkthrough lives in [../QUICKSTART.md](../QUICKSTART.md).

**What exactly does it generate?**
Static configuration files for the tool you pick — for example a `.claude/`
directory for Claude, a `.cursor/` directory for Cursor, and so on. The files are
plain text config that your chosen assistant reads. Nothing is generated at
runtime while you code.

**Do I need an API key or an internet connection?**
No. prompticorn does not call an LLM. It generates static config files on your
machine from the bundled library, so there is no API key to configure and no
per-generation cost.

**Will it overwrite my existing configuration?**
When you generate for a tool, prompticorn writes that tool's config artifacts. If
you switch to a different tool, it cleans up the previous tool's artifacts so you
are not left with stale config from a tool you no longer use. If you keep
important hand edits in those directories, commit them first so you can review any
changes. See [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) if something looks off.

**How do I switch from one tool to another?**
Run `prompticorn init` again and pick the new tool. The previous tool's generated
artifacts are removed and the new tool's files are written in their place.

---

## Individual developer

**How do I regenerate after the library is updated?**
Re-run `prompticorn init` and follow the prompts. Because output is generated from
the library, regenerating picks up the latest agents, workflows, and skills. Since
the generated files are meant to be committed, review the diff before committing so
you can see what changed.

**How do I choose which agents and skills are included?**
`prompticorn init` is interactive and prompts you through the selection. Make your
choices at the prompts rather than editing generated files by hand — that way your
selections survive the next regeneration.

**Is there a minimal versus a verbose output option?**
Yes — the library supports leaner and more detailed variants of the emitted
config. Choose the variant you want during the interactive `prompticorn init` run.
Pick minimal when you want a tight footprint, or the fuller variant when you want
the extra guidance inline.

**How does it work with my programming language?**
The library ships 26 language convention sets. During `prompticorn init` you
select the language conventions relevant to your project, and they are woven into
the generated config so your assistant follows the right idioms.

**How are skills represented in the output?**
Each skill is emitted as a `SKILL.md` file inside its own folder. That keeps skills
self-contained and easy to inspect in the generated tree.

**Can I use two tools at once?**
prompticorn is built around a single active tool per generation, and switching
tools cleans up the previous tool's artifacts. If you genuinely need two tools in
one repo, keep in mind that a later `prompticorn init` for a different tool will
remove the earlier tool's generated files. Commit your work between runs so nothing
is lost, and see [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for recovery tips.

**Should I edit the generated files directly?**
Prefer regenerating over hand-editing. The generated files are outputs of the
library, so manual edits can be overwritten on the next `prompticorn init`. If you
need different behavior, change your selections at the prompts.

---

## Team lead / adopter

**How do I standardize configuration across my team?**
Generate the config once with `prompticorn init`, commit it to the repository, and
everyone on the team gets the same agents, workflows, skills, and language
conventions the moment they clone. The shared library is the single source of
truth, so there is one place to reason about.

**Should the generated config be committed to the repo?**
Yes. The output is designed to be committed. Checking it in gives you reviewable
diffs, reproducible setup, and a consistent experience for every contributor.

**How do we keep everyone's tools in sync as the library evolves?**
When the library updates, one person re-runs `prompticorn init`, reviews the diff,
and commits the regenerated config. Because the files are in the repo, a normal
pull brings everyone up to date — no separate distribution step.

**What does onboarding a new team member look like?**
They clone the repo and open it in whichever supported assistant your team uses;
the committed config is already there. Point them at
[../QUICKSTART.md](../QUICKSTART.md) and [GETTING_STARTED.md](GETTING_STARTED.md)
for orientation.

**Different people on my team use different assistants — can we support that?**
prompticorn generates for one tool per run and cleans up the previous tool's
artifacts when you switch, so a single committed tree targets one assistant.
Standardize on one tool for the shared committed config, and let individuals who
prefer another assistant regenerate locally, understanding a switch replaces the
committed tool's files. See [TOOLS.md](TOOLS.md) for what each tool expects.

**We have a monorepo with multiple languages — how do we handle that?**
The library includes 26 language convention sets, so you can select the conventions
that match the languages in your monorepo during `prompticorn init`. Choose the
combination that reflects your codebase so the generated guidance covers each
language your team works in.

**How do we review prompticorn changes in pull requests?**
Because the config is committed static text, every regeneration shows up as a
normal diff. Treat those diffs like any other change: review, discuss, and merge
through your usual PR process.

---

## Contributor

**Where is the source of truth?**
The shared prompt library is the source of truth — the 26 primary agents, ~100
workflows, 96 skills, and 26 language convention sets. Generated per-tool config is
an output of that library, never the place to make lasting changes.

**How do I add a new skill?**
Add it to the library following the existing skill structure — each skill is
authored so it emits as a `SKILL.md` file in its own folder. Start with
[../../CONTRIBUTING.md](../../CONTRIBUTING.md) for the workflow and conventions.

**How do I add a new agent or workflow?**
Agents and workflows also live in the library. Follow the patterns of the existing
entries and the guidance in [../../CONTRIBUTING.md](../../CONTRIBUTING.md) so your
addition flows through generation into every supported tool.

**How do I add support for a new tool (a new builder)?**
Each supported assistant has a builder that knows how to emit that tool's config.
The builder docs under [../builders/](../builders/) explain the builder API and
implementation pattern, and [../../CONTRIBUTING.md](../../CONTRIBUTING.md) covers
how a new builder fits into the project. Model your builder on an existing one and
wire it in so `prompticorn init` can target the new tool.

**How do the tests work?**
Two complementary layers protect the output. Golden output tests assert that
generation produces exactly the expected files, so unintended changes surface as
test failures. Content-quality gates check that the emitted content meets the
library's standards. Run the suite before opening a pull request.

**How do I keep the golden tests green when my change is intentional?**
If your change deliberately alters generated output, update the golden fixtures to
match the new expected output as part of the same change, and make sure the
content-quality gates still pass. Explain the intended output change in your pull
request so reviewers can confirm it.

**What Python version do I need to contribute?**
Python 3.10 or newer.

**Where should I start reading?**
Read [../../CONTRIBUTING.md](../../CONTRIBUTING.md) first for the contribution
workflow, then the builder guides in [../builders/](../builders/) if you are
extending tool support. [../ARCHITECTURE.md](../ARCHITECTURE.md) gives the
big-picture view of how the library and builders fit together.

---

## Still stuck?

If your question is not covered here, check
[../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues, or the broader
docs index at [../INDEX.md](../INDEX.md).
