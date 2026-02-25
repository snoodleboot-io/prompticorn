<!-- path: README.md -->
# Dev Prompt Library

A single source of truth for AI coding assistant rules, synced automatically
into Kilo Code and Cline project structures.

## Structure

```
prompt-library/
├── flat/                        ← THE SOURCE OF TRUTH — edit files here
│   ├── core-system.md           ← always-on base behaviors
│   ├── core-conventions.md      ← ⚙️ fill-ahead: your project's coding standards
│   ├── architect-*.md           ← Kilo Architect mode / planning tasks
│   ├── code-*.md                ← Kilo Code mode / implementation tasks
│   ├── review-*.md              ← Kilo Review mode
│   ├── debug-*.md               ← Kilo Debug mode
│   ├── ask-*.md                 ← Kilo Ask mode / docs and Q&A
│   └── orchestrator-*.md        ← Kilo Orchestrator mode / devops and process
│
├── kilo/                        ← Auto-generated — do not edit directly
│   └── .kilocode/
│       ├── rules/               ← loaded in ALL Kilo modes
│       ├── rules-architect/     ← loaded only in Architect mode
│       ├── rules-code/          ← loaded only in Code mode
│       ├── rules-review/        ← loaded only in Review mode
│       ├── rules-debug/         ← loaded only in Debug mode
│       ├── rules-ask/           ← loaded only in Ask mode
│       └── rules-orchestrator/  ← loaded only in Orchestrator mode
│
├── cline/                       ← Auto-generated — do not edit directly
│   └── .clinerules              ← all rules concatenated into one file
│
└── sync.sh                      ← rebuilds kilo/ and cline/ from flat/
```

## Workflow

### 1. Initial Setup

Edit `flat/core-conventions.md` and fill in all `{{PLACEHOLDER}}` values for your project.
Then run the sync script:

```bash
./sync.sh
```

### 2. Using with Kilo Code

Copy the `.kilocode/` directory into your project root:

```bash
cp -r kilo/.kilocode my-project/.kilocode
```

Or symlink for automatic updates:

```bash
ln -s ~/dev-prompts/kilo/.kilocode my-project/.kilocode
```

Commit `.kilocode/` to your repo so your team gets the same behavior.

Switch modes in the Kilo UI — the right rules load automatically. No prompting needed.

### 3. Using with Cline

Copy `.clinerules` into your project root:

```bash
cp cline/.clinerules my-project/.clinerules
```

Commit it to the repo.

Also paste `flat/core-system.md` into Cline's global Custom Instructions
(VS Code → Cline → Settings → Custom Instructions) once — applies to all projects.

### 4. Editing Rules

Always edit files in `flat/` — never edit `kilo/` or `cline/` directly.

After any edit:

```bash
./sync.sh                 # rebuild both
./sync.sh --kilo-only     # rebuild kilo/ only
./sync.sh --cline-only    # rebuild cline/ only
./sync.sh --dry-run       # preview what would change
```

### 5. Per-Project Overrides

To customize rules for a specific project without touching the global library:
- For Kilo: edit the `.kilocode/rules/` files directly in that project after copying
- For Cline: append to `.clinerules` under a `## PROJECT-SPECIFIC RULES` section

These project-local edits will be overwritten if you re-run `sync.sh` and re-copy.
To preserve them, keep project overrides in a separate section and re-apply after sync.

## Marker Convention

| Marker | Meaning | When |
|--------|---------|------|
| `{{PLACEHOLDER}}` | Fill ahead of time | Edit `core-conventions.md` at project setup |
| `[describe this]` | Provide at runtime | When invoking a task in Kilo/Cline |

## File Naming Convention in flat/

Files are named `{mode}-{topic}.md` so the sync script knows where each one belongs:

| Prefix | Goes to |
|--------|---------|
| `core-` | `.kilocode/rules/` (all modes) and Cline header |
| `architect-` | `.kilocode/rules-architect/` |
| `code-` | `.kilocode/rules-code/` |
| `review-` | `.kilocode/rules-review/` |
| `debug-` | `.kilocode/rules-debug/` |
| `ask-` | `.kilocode/rules-ask/` |
| `orchestrator-` | `.kilocode/rules-orchestrator/` |

To add a new rule file: create `flat/{mode}-{topic}.md`, add a `copy` line
to `sync.sh`, then run `./sync.sh`.
