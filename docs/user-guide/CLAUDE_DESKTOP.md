# Using prompticorn with Claude Desktop

Claude Desktop is not a repo-config assistant like Cursor or Cline. It has **no
on-disk directory it reads agents or skills from** — its only file-based config
is `claude_desktop_config.json`, which wires up MCP servers (something prompticorn
does not generate). So there is no "Claude Desktop builder"; instead there are two
supported paths to get prompticorn's content into the Claude desktop experience.

## Path 1 — Claude Code (recommended)

If you use **Claude Code** from the desktop app (or the terminal), prompticorn
already targets it. Generate the Claude output and Claude Code picks it up from
the repo:

```bash
prompticorn switch claude   # writes .claude/ and CLAUDE.md
```

- Agents → `.claude/agents/`
- Skills → `.claude/skills/<name>/SKILL.md`
- Conventions → `CLAUDE.md`

This is the fullest integration: agents, skills, and conventions all reach Claude
Code without any manual upload. See [QUICKSTART.md](../QUICKSTART.md) for the full
setup walkthrough.

## Path 2 — Upload skills to the native app (manual)

The **native Claude Desktop chat app** (and claude.ai) accepts custom Agent
Skills only as **zip uploads** through **Settings → Features** — one zip per
skill. prompticorn can package the skills it generates into exactly that shape:

```bash
# 1. Generate skills (any tool that emits SKILL.md folders works)
prompticorn switch claude

# 2. Package them into upload-ready zips
prompticorn package-skills
#    -> dist/claude-desktop-skills/<name>.zip  (one per skill)
```

Each zip contains the skill folder at its root (`<name>/SKILL.md`) with the
`name`/`description` frontmatter claude.ai requires. Then, in claude.ai or Claude
Desktop:

1. Open **Settings → Features** (requires a plan with custom Skills + code
   execution enabled).
2. Upload each `<name>.zip`.

### Options

```bash
prompticorn package-skills --source .claude/skills --output dist/skills
```

- `--source` — directory of emitted skills (`<name>/SKILL.md` folders). Defaults
  to the first of `.claude/skills`, `.agents/skills`, `.github/skills`.
- `--output` — where the `.zip` files are written (default
  `dist/claude-desktop-skills/`).

### Notes and limits

- **One skill per zip** — this is claude.ai's required format, not a prompticorn
  choice.
- Skill `name` must be lowercase letters/digits/hyphens and must not contain the
  reserved words *anthropic* or *claude*; any skill that violates this is skipped
  with a warning rather than packaged into an archive that would fail to upload.
- claude.ai currently caps custom skills at **20** per account, so upload the
  skills most relevant to your work rather than all of them.
- Uploaded skills are per-user and do **not** sync to the Claude API or Claude
  Code — Path 1 remains the way to share skills through a repo.

## What about `claude_desktop_config.json`?

That file configures **MCP servers**, not agents or skills. prompticorn does not
generate MCP servers, so it does not write this file. If you add MCP servers,
that is separate from prompticorn's output.
