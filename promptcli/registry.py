"""
registry.py
Single source of truth for all modes, their prompt files, and output ordering.

To add a new mode:
  1. Add it to MODES (key → display label)
  2. Add its files to MODE_FILES (key → ordered list of filenames from prompts/)
  3. Add entries to CONCAT_ORDER for tools that use a flat concatenated output

To add a new file to an existing mode:
  1. Drop the .md file in prompts/
  2. Add the filename to MODE_FILES[mode]
  3. Add a CONCAT_ORDER entry with the section label
"""

from pathlib import Path

# ── Prompt file directory ─────────────────────────────────────────────────────
# Resolved relative to this file so the CLI works from any working directory.
PROMPTS_DIR = Path(__file__).parent / "prompts"

# ── Always-on files ───────────────────────────────────────────────────────────
# Loaded in every mode (Kilo: rules/), or at the top of concatenated outputs.
ALWAYS_ON: list[str] = [
    "core-system.md",
    "core-conventions.md",
]

# ── Mode registry ─────────────────────────────────────────────────────────────
# key       → used as directory name suffix (rules-{key}) and CLI argument
# display   → human-readable label for headers and list output
MODES: dict[str, str] = {
    "architect":   "Architect",
    "test":        "Test",
    "refactor":    "Refactor",
    "document":    "Document",
    "explain":     "Explain",
    "migration":   "Migration",
    "code":        "Code",
    "review":      "Review",
    "debug":       "Debug",
    "ask":         "Ask",
    "security":    "Security",
    "compliance":  "Compliance",
    "orchestrator": "Orchestrator",
}

# ── Files per mode ────────────────────────────────────────────────────────────
# Order within a mode matters for concatenated outputs — earlier = higher priority.
MODE_FILES: dict[str, list[str]] = {
    "architect": [
        "architect-scaffold.md",
        "architect-task-breakdown.md",
        "architect-data-model.md",
    ],
    "test": [
        "test-strategy.md",
    ],
    "refactor": [
        "refactor-strategy.md",
        "code-refactor.md",
    ],
    "document": [
        "document-strategy.md",
    ],
    "explain": [
        "explain-strategy.md",
    ],
    "migration": [
        "migration-strategy.md",
        "code-migration.md",
        "code-dependency-upgrade.md",
    ],
    "code": [
        "code-feature.md",
        "code-boilerplate.md",
        "code-house-style.md",
    ],
    "review": [
        "review-code.md",
        "review-performance.md",
        "review-accessibility.md",
    ],
    "debug": [
        "debug-root-cause.md",
        "debug-log-analysis.md",
        "debug-rubber-duck.md",
    ],
    "ask": [
        "ask-docs.md",
        "ask-testing.md",
        "ask-decision-log.md",
    ],
    "security": [
        "security-review.md",
    ],
    "compliance": [
        "compliance-review.md",
    ],
    "orchestrator": [
        "orchestrator-devops.md",
        "orchestrator-meta.md",
    ],
}

# ── Concatenated output order ─────────────────────────────────────────────────
# Used by Cline, Cursor (legacy), and Copilot (always-on file).
# Each entry: (section_label, filename)
# Filename must be in ALWAYS_ON or appear in some MODE_FILES list.
CONCAT_ORDER: list[tuple[str, str]] = [
    ("CORE BEHAVIORS",       "core-system.md"),
    ("CONVENTIONS",          "core-conventions.md"),
    ("PLANNING / ARCHITECT", "architect-scaffold.md"),
    ("TASK BREAKDOWN",       "architect-task-breakdown.md"),
    ("DATA MODEL",           "architect-data-model.md"),
    ("FEATURE IMPLEMENTATION", "code-feature.md"),
    ("BOILERPLATE",          "code-boilerplate.md"),
    ("HOUSE STYLE",          "code-house-style.md"),
    ("TESTING",              "test-strategy.md"),
    ("REFACTORING",          "refactor-strategy.md"),
    ("MIGRATION",            "migration-strategy.md"),
    ("DOCUMENTATION",        "document-strategy.md"),
    ("EXPLAIN",              "explain-strategy.md"),
    ("CODE REVIEW",          "review-code.md"),
    ("PERFORMANCE REVIEW",   "review-performance.md"),
    ("ACCESSIBILITY REVIEW", "review-accessibility.md"),
    ("SECURITY REVIEW",      "security-review.md"),
    ("COMPLIANCE REVIEW",    "compliance-review.md"),
    ("DEBUGGING",            "debug-root-cause.md"),
    ("LOG ANALYSIS",         "debug-log-analysis.md"),
    ("RUBBER DUCK",          "debug-rubber-duck.md"),
    ("DOCS GENERATION",      "ask-docs.md"),
    ("TEST GENERATION",      "ask-testing.md"),
    ("DECISION LOG",         "ask-decision-log.md"),
    ("DEVOPS",               "orchestrator-devops.md"),
    ("META / PROCESS",       "orchestrator-meta.md"),
]

# ── Copilot applyTo globs ────────────────────────────────────────────────────
# Controls which files each mode's instruction file activates for in Copilot.
COPILOT_APPLY: dict[str, str] = {
    "architect":   "**",
    "test":        "**/*.test.*,**/*.spec.*,**/tests/**",
    "refactor":    "**",
    "document":    "**/*.md,**/*.ts,**/*.py,**/*.go",
    "explain":     "**",
    "migration":   "**",
    "code":        "**",
    "review":      "**",
    "debug":       "**",
    "ask":         "**",
    "security":    "**",
    "compliance":  "**",
    "orchestrator": "**/*.yml,**/*.yaml,**/Dockerfile,**/.github/**",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def prompt_path(filename: str) -> Path:
    """Absolute path to a prompt file."""
    return PROMPTS_DIR / filename


def prompt_body(filename: str) -> str:
    """
    Read a prompt file and strip the two-line filename header comment
    that appears at the top of files carried over from the old flat/ format.
    Returns the content ready to embed in any output file.
    """
    path = prompt_path(filename)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    # Strip lines that are pure header comments (# filename or <!-- path: ... -->)
    start = 0
    for i, line in enumerate(lines[:3]):
        stripped = line.strip()
        if stripped.startswith("# ") and (
            stripped.endswith(".md") or "Behavior when" in stripped
        ):
            start = i + 1
        elif stripped.startswith("<!--") and stripped.endswith("-->"):
            start = i + 1
    return "".join(lines[start:])


def dest_name(mode_key: str, filename: str, ext: str = ".md") -> str:
    """
    Strip the mode prefix from a filename for use as a destination name.
    e.g. architect-scaffold.md  → scaffold.md
         test-strategy.md       → strategy.md
         security-review.md     → review.md
    Then swap extension if needed (e.g. .md → .mdc for Cursor).
    """
    stem = filename
    prefix = f"{mode_key}-"
    if stem.startswith(prefix):
        stem = stem[len(prefix):]
    if ext != ".md":
        stem = stem.replace(".md", ext)
    return stem


def validate() -> list[str]:
    """
    Check every registered filename exists in prompts/.
    Returns a list of error strings (empty = all good).
    """
    errors: list[str] = []
    all_registered: set[str] = set(ALWAYS_ON)
    for files in MODE_FILES.values():
        all_registered.update(files)

    for fname in all_registered:
        if not prompt_path(fname).exists():
            errors.append(f"MISSING: {fname}")

    # Check CONCAT_ORDER references valid files
    for label, fname in CONCAT_ORDER:
        if fname not in all_registered:
            errors.append(f"CONCAT_ORDER '{label}': '{fname}' not in any mode or ALWAYS_ON")

    # Check for orphaned files in prompts/ not in registry
    registered_names = all_registered
    for p in PROMPTS_DIR.glob("*.md"):
        if p.name not in registered_names:
            errors.append(f"ORPHAN: {p.name} exists in prompts/ but is not registered")

    return errors
