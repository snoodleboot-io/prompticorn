# Tool Guide

prompticorn generates AI-assistant configuration from a single shared library so
that every tool you use is driven by the same underlying rules, agents, and
skills. Instead of hand-maintaining a different config format for each assistant,
you author once and let prompticorn emit the right files for each tool.

## How tool selection works

1. Run `prompticorn init` in the repository you want to configure.
2. Pick the tool (or tools) you use from the list.
3. prompticorn writes that tool's config files directly into your repo, using
   the file names and locations each tool expects.

The rest of this guide is a per-tool reference. For each tool it lists what
prompticorn generates, the exact paths those artifacts land at, and how you
activate or consume the output inside that tool.

### A note on skills

Most tools receive "skills" as a folder-per-skill layout:
`<base>/skills/<name>/SKILL.md`, where each `SKILL.md` carries YAML frontmatter.
A few tools are exceptions and are called out in their own sections:

- **Cline** and **Cursor** consume a single concatenated rules file, so their
  skills still emit (to `.cline/skills` and `.cursor/skills`) but the tool reads
  the combined rules file rather than individual skill folders.
- **Aider** expresses conventions through `CONVENTIONS.md` rather than a skills
  folder.
- **GitHub Copilot Chat** has no skill primitive, so skills are dropped for it.

---

## Kilo (CLI and IDE)

Kilo ships in two variants, and prompticorn treats them as separate tool ids
that write to different locations. Pick the one that matches how you run Kilo.

### Kilo CLI

Command-line variant of Kilo.

Generates:

- `.opencode/`

Using it: run Kilo from the command line in the repo root; it reads its
configuration from the `.opencode/` directory prompticorn populated.

### Kilo IDE

Editor-integrated variant of Kilo.

Generates:

- `.kilo/`

Using it: open the repo in the Kilo IDE; it picks up configuration from the
`.kilo/` directory. Note that the CLI uses `.opencode/` while the IDE uses
`.kilo/`, so if you use both you will have both directories.

---

## Claude (Claude Code)

Anthropic's Claude Code assistant, driven by a project directory and a top-level
instructions file.

Generates:

- `.claude/`
- `CLAUDE.md`

Using it: Claude Code automatically loads `CLAUDE.md` and the contents of
`.claude/` when it runs in the repository. Skills are emitted under `.claude/`
as `skills/<name>/SKILL.md` folders.

Using it: no manual step is required beyond running Claude Code in the repo root
so it can find these files.

---

## Cline

VS Code extension that reads a single rules file.

Generates:

- `.clinerules`

Using it: Cline reads `.clinerules` from the repo root automatically. Because
Cline consumes one concatenated rules file, skills are combined into that file
rather than read as separate folders (they still emit to `.cline/skills`).

---

## Cursor

The Cursor editor, which supports both a rules directory and a legacy rules
file.

Generates:

- `.cursor/`
- `.cursorrules`

Using it: open the repo in Cursor; it reads the `.cursor/` directory and the
`.cursorrules` file. As with Cline, Cursor uses a single concatenated rules
file, so skills still emit (to `.cursor/skills`) but the tool reads the combined
rules rather than individual skill folders.

---

## GitHub Copilot

GitHub Copilot's repository-level instructions plus its agent skills.

Generates:

- `.github/copilot-instructions.md`
- Agent skills at `.github/skills/<name>/SKILL.md`

Using it: Copilot picks up `.github/copilot-instructions.md` as repository
instructions, and reads each skill from its own folder under `.github/skills/`.
No activation step is needed beyond committing these files to the repo.

---

## GitHub Copilot Chat

The chat-oriented Copilot surface, which uses agents, prompts, and instructions
directories.

Generates:

- `.github/agents/`
- `.github/prompts/`
- `.github/instructions/`

Using it: Copilot Chat reads its agents, prompts, and instructions from these
directories under `.github/`.

Gotcha: Copilot Chat has no skill primitive, so skills are dropped for this tool.
If you rely on skills, use a tool that supports them.

---

## Roo Code

The Roo Code assistant, which uses a configuration directory and a modes file.

Generates:

- `.roo/`
- `.roomodes`

Using it: Roo Code reads the `.roo/` directory and the `.roomodes` file from the
repo root. Skills emit under the tool's base as `skills/<name>/SKILL.md` folders.

---

## Junie

The Junie assistant, configured from its own directory.

Generates:

- `.junie/`

Using it: Junie reads its configuration from the `.junie/` directory in the repo.
Skills emit as `skills/<name>/SKILL.md` folders under that base.

---

## Zed

The Zed editor's agent configuration.

Generates:

- `.agents/`

Using it: Zed reads agent configuration from the `.agents/` directory. Skills
emit as `skills/<name>/SKILL.md` folders under the tool's base.

---

## Gemini CLI

Google's Gemini command-line assistant.

Generates:

- `.gemini/`

Using it: run the Gemini CLI in the repo; it reads its configuration from the
`.gemini/` directory. Skills emit as `skills/<name>/SKILL.md` folders under that
base.

---

## Amazon Q

Amazon's Q assistant, configured from its own directory.

Generates:

- `.amazonq/`

Using it: Amazon Q reads its configuration from the `.amazonq/` directory in the
repo. Skills emit as `skills/<name>/SKILL.md` folders under that base.

---

## Windsurf

The Windsurf editor's rules and configuration.

Generates:

- `.windsurf/`

Using it: Windsurf reads its configuration from the `.windsurf/` directory.
Skills emit as `skills/<name>/SKILL.md` folders under that base.

Gotcha: Windsurf caps rule files at roughly 12,000 characters. If your rules are
large, expect Windsurf to truncate or reject content beyond that limit, so keep
individual rule files within the cap.

---

## Continue

The Continue assistant, configured from its own directory.

Generates:

- `.continue/`

Using it: Continue reads its configuration from the `.continue/` directory in
the repo. Skills emit as `skills/<name>/SKILL.md` folders under that base.

---

## Aider

The Aider pair-programming assistant, driven by a config file and a conventions
file.

Generates:

- `.aider.conf.yml`
- `CONVENTIONS.md`

Using it: Aider reads `.aider.conf.yml` for its settings and `CONVENTIONS.md`
for project conventions. Rather than a skills folder, Aider expresses its
conventions through `CONVENTIONS.md`.

---

## Codex

The Codex assistant, which uses an agents directory alongside its own config
directory.

Generates:

- `.agents/`
- `.codex/`

Using it: Codex reads agent definitions from `.agents/` and its own
configuration from `.codex/`. Skills emit as `skills/<name>/SKILL.md` folders
under the tool's base.

---

## Summary of artifact paths

| Tool | Generates |
|------|-----------|
| Kilo CLI | `.opencode/` |
| Kilo IDE | `.kilo/` |
| Claude (Claude Code) | `.claude/`, `CLAUDE.md` |
| Cline | `.clinerules` |
| Cursor | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/skills/<name>/SKILL.md` |
| GitHub Copilot Chat | `.github/agents/`, `.github/prompts/`, `.github/instructions/` |
| Roo Code | `.roo/`, `.roomodes` |
| Junie | `.junie/` |
| Zed | `.agents/` |
| Gemini CLI | `.gemini/` |
| Amazon Q | `.amazonq/` |
| Windsurf | `.windsurf/` (rule files capped at ~12,000 chars) |
| Continue | `.continue/` |
| Aider | `.aider.conf.yml`, `CONVENTIONS.md` |
| Codex | `.agents/`, `.codex/` |
