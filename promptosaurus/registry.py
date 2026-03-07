"""
registry.py
Single source of truth for all modes, their prompt files, and output ordering.

To add a new mode:
  1. Add it to modes (key → display label)
  2. Add its files to mode_files (key → ordered list of filenames from prompts/)
  3. Add entries to concat_order for tools that use a flat concatenated output

To add a new file to an existing mode:
  1. Drop the .md file in prompts/
  2. Add the filename to mode_files[mode]
  3. Add a concat_order entry with the section label
"""

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, computed_field, field_validator, model_validator


# ── Module-level cached function ─────────────────────────────────────────────
@lru_cache(maxsize=32)
def _prompt_body_cached(prompts_dir: Path, filename: str) -> str:
    """Read and process a prompt file (cached for performance)."""
    path = prompts_dir / filename
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    # Strip lines that are pure header comments (# filename or <!-- path: ... -->)
    start = 0
    for i, line in enumerate(lines[:3]):
        stripped = line.strip()
        if stripped.startswith("# ") and (stripped.endswith(".md") or "Behavior when" in stripped):
            start = i + 1
        elif stripped.startswith("<!--") and stripped.endswith("-->"):
            start = i + 1
    return "".join(lines[start:])


def _dest_name(mode_key: str, filename: str, ext: str = ".md") -> str:
    """Strip the mode prefix from a filename."""
    stem = filename
    prefix = f"{mode_key}-"
    if stem.startswith(prefix):
        stem = stem[len(prefix) :]
    if ext != ".md":
        stem = stem.replace(".md", ext)
    return stem


class Registry(BaseModel):
    """Registry of all modes, prompt files, and output ordering."""

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
    )

    # ── Prompt file directory ─────────────────────────────────────────────────
    prompts_dir: Path = Path(__file__).parent / "prompts"

    # ── Always-on files ───────────────────────────────────────────────────────
    always_on: list[str] = [
        "agents/core/core-system.md",
        "agents/core/core-conventions.md",
        "agents/core/core-session.md",
        # Language-specific conventions (user includes relevant ones)
        "agents/core/core-conventions-typescript.md",
        "agents/core/core-conventions-javascript.md",
        "agents/core/core-conventions-php.md",
        "agents/core/core-conventions-ruby.md",
        "agents/core/core-conventions-python.md",
        "agents/core/core-conventions-java.md",
        "agents/core/core-conventions-csharp.md",
        "agents/core/core-conventions-golang.md",
        "agents/core/core-conventions-rust.md",
        "agents/core/core-conventions-r.md",
        "agents/core/core-conventions-elixir.md",
        "agents/core/core-conventions-elm.md",
        "agents/core/core-conventions-c.md",
        "agents/core/core-conventions-cpp.md",
        "agents/core/core-conventions-scala.md",
        "agents/core/core-conventions-kotlin.md",
        "agents/core/core-conventions-swift.md",
        "agents/core/core-conventions-objc.md",
        "agents/core/core-conventions-dart.md",
        "agents/core/core-conventions-julia.md",
        "agents/core/core-conventions-haskell.md",
        "agents/core/core-conventions-clojure.md",
        "agents/core/core-conventions-fsharp.md",
        "agents/core/core-conventions-shell.md",
        "agents/core/core-conventions-groovy.md",
        "agents/core/core-conventions-lua.md",
        "agents/core/core-conventions-sql.md",
        "agents/core/core-conventions-terraform.md",
        "agents/core/core-conventions-html.md",
    ]

    # ── Mode registry ───────────────────────────────────────────────────────
    # TODO: Discover This
    modes: dict[str, str] = {
        "architect": "Architect",
        "test": "Test",
        "refactor": "Refactor",
        "document": "Document",
        "explain": "Explain",
        "migration": "Migration",
        "code": "Code",
        "review": "Review",
        "debug": "Debug",
        "ask": "Ask",
        "security": "Security",
        "compliance": "Compliance",
        "orchestrator": "Orchestrator",
        "enforcement": "Enforcement",
        "planning": "Planning",
    }

    # ── Files per mode ───────────────────────────────────────────────────────
    # TODO: This should be auto-discoverable
    mode_files: dict[str, list[str]] = {
        "architect": [
            "agents/architect/subagents/architect-scaffold.md",
            "agents/architect/subagents/architect-task-breakdown.md",
            "agents/architect/subagents/architect-data-model.md",
        ],
        "test": [
            "agents/test/subagents/test-strategy.md",
        ],
        "refactor": [
            "agents/refactor/subagents/refactor-strategy.md",
            "agents/code/subagents/code-refactor.md",
        ],
        "document": [
            "agents/document/subagents/document-strategy-for-applications.md",
        ],
        "explain": [
            "agents/explain/subagents/explain-strategy.md",
        ],
        "migration": [
            "agents/migration/subagents/migration-strategy.md",
            "agents/code/subagents/code-migration.md",
            "agents/code/subagents/code-dependency-upgrade.md",
        ],
        "code": [
            "agents/code/subagents/code-feature.md",
            "agents/code/subagents/code-boilerplate.md",
            "agents/code/subagents/code-house-style.md",
        ],
        "review": [
            "agents/review/subagents/review-code.md",
            "agents/review/subagents/review-performance.md",
            "agents/review/subagents/review-accessibility.md",
        ],
        "debug": [
            "agents/debug/subagents/debug-root-cause.md",
            "agents/debug/subagents/debug-log-analysis.md",
            "agents/debug/subagents/debug-rubber-duck.md",
            "agents/core/core-session-troubleshooting.md",
        ],
        "ask": [
            "agents/ask/subagents/ask-docs.md",
            "agents/ask/subagents/ask-testing.md",
            "agents/ask/subagents/ask-decision-log.md",
            "agents/core/core-decision-log-template.md",
        ],
        "security": [
            "agents/security/subagents/security-review.md",
        ],
        "compliance": [
            "agents/compliance/subagents/compliance-review.md",
        ],
        "orchestrator": [
            "agents/orchestrator/subagents/orchestrator-devops.md",
            "agents/orchestrator/subagents/orchestrator-meta.md",
            "agents/orchestrator/subagents/orchestrator-pr-description.md",
        ],
        "enforcement": [
            "agents/enforcement/enforcement.md",
        ],
        "planning": [
            "agents/project_planning/planning.md",
        ],
    }

    # ── Concatenated output order ───────────────────────────────────────────
    concat_order: list[tuple[str, str]] = [
        ("CORE BEHAVIORS", "agents/core/core-system.md"),
        ("CONVENTIONS", "agents/core/core-conventions.md"),
        ("SESSION MANAGEMENT", "agents/core/core-session.md"),
        ("SESSION TROUBLESHOOTING", "agents/core/core-session-troubleshooting.md"),
        ("TYPESCRIPT", "agents/core/core-conventions-typescript.md"),
        ("PYTHON", "agents/core/core-conventions-python.md"),
        ("GO", "agents/core/core-conventions-golang.md"),
        ("SQL", "agents/core/core-conventions-sql.md"),
        ("PLANNING / ARCHITECT", "agents/architect/subagents/architect-scaffold.md"),
        ("TASK BREAKDOWN", "agents/architect/subagents/architect-task-breakdown.md"),
        ("DATA MODEL", "agents/architect/subagents/architect-data-model.md"),
        ("FEATURE IMPLEMENTATION", "agents/code/subagents/code-feature.md"),
        ("BOILERPLATE", "agents/code/subagents/code-boilerplate.md"),
        ("HOUSE STYLE", "agents/code/subagents/code-house-style.md"),
        ("TESTING", "agents/test/subagents/test-strategy.md"),
        ("REFACTORING", "agents/refactor/subagents/refactor-strategy.md"),
        ("MIGRATION", "agents/migration/subagents/migration-strategy.md"),
        ("DOCUMENTATION", "agents/document/subagents/document-strategy-for-applications.md"),
        ("EXPLAIN", "agents/explain/subagents/explain-strategy.md"),
        ("CODE REVIEW", "agents/review/subagents/review-code.md"),
        ("PERFORMANCE REVIEW", "agents/review/subagents/review-performance.md"),
        ("ACCESSIBILITY REVIEW", "agents/review/subagents/review-accessibility.md"),
        ("SECURITY REVIEW", "agents/security/subagents/security-review.md"),
        ("COMPLIANCE REVIEW", "agents/compliance/subagents/compliance-review.md"),
        ("DEBUGGING", "agents/debug/subagents/debug-root-cause.md"),
        ("LOG ANALYSIS", "agents/debug/subagents/debug-log-analysis.md"),
        ("RUBBER DUCK", "agents/debug/subagents/debug-rubber-duck.md"),
        ("DOCS GENERATION", "agents/ask/subagents/ask-docs.md"),
        ("TEST GENERATION", "agents/ask/subagents/ask-testing.md"),
        ("DECISION LOG", "agents/ask/subagents/ask-decision-log.md"),
        ("DECISION LOG TEMPLATE", "agents/core/core-decision-log-template.md"),
        ("DEVOPS", "agents/orchestrator/subagents/orchestrator-devops.md"),
        ("META / PROCESS", "agents/orchestrator/subagents/orchestrator-meta.md"),
        ("ENFORCEMENT", "agents/enforcement/enforcement.md"),
        ("PLANNING", "agents/project_planning/planning.md"),
    ]

    # ── Default ignore patterns for all agents ─────────────────────────────
    default_ignore_patterns: list[str] = [
        # Python cache
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        # Dependencies
        "node_modules/",
        ".venv/",
        "venv/",
        "env/",
        "vendor/",
        "packages/",
        # Build outputs
        "dist/",
        "build/",
        "*.egg-info/",
        "*.egg",
        "target/",
        "out/",
        # IDE
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*~",
        # Secrets
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "*.secret",
        "secrets/",
        "credentials/",
        # Logs
        "*.log",
        "logs/",
        # OS
        ".DS_Store",
        "Thumbs.db",
    ]

    # ── Copilot applyTo globs ───────────────────────────────────────────────
    copilot_apply: dict[str, str] = {
        "architect": "**",
        "test": "**/*.test.*,**/*.spec.*,**/tests/**",
        "refactor": "**",
        "document": "**/*.md,**/*.ts,**/*.py,**/*.go",
        "explain": "**",
        "migration": "**",
        "code": "**",
        "review": "**",
        "debug": "**",
        "ask": "**",
        "security": "**",
        "compliance": "**",
        "orchestrator": "**/*.yml,**/*.yaml,**/Dockerfile,**/.github/**",
    }

    # ── Computed properties ────────────────────────────────────────────────

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_registered_files(self) -> set[str]:
        """All files registered in the registry."""
        files = set(self.always_on)
        for file_list in self.mode_files.values():
            files.update(file_list)
        return files

    # ── Validators ───────────────────────────────────────────────────────────

    @field_validator("prompts_dir")
    @classmethod
    def prompts_dir_must_exist(cls, v: Path) -> Path:
        """Verify prompts directory exists."""
        if not v.exists():
            raise ValueError(f"Prompts directory does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Prompts path is not a directory: {v}")
        return v

    @field_validator("modes")
    @classmethod
    def modes_must_not_be_empty(cls, v: dict[str, str]) -> dict[str, str]:
        """Verify modes dictionary is not empty."""
        if not v:
            raise ValueError("Modes dictionary cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_all_files_exist(self) -> "Registry":
        """Check every registered filename exists in prompts/."""
        errors: list[str] = []

        for fname in self.all_registered_files:
            if not (self.prompts_dir / fname).exists():
                errors.append(f"MISSING: {fname}")

        for label, fname in self.concat_order:
            if fname not in self.all_registered_files:
                errors.append(f"CONCAT_ORDER '{label}': '{fname}' not in any mode or ALWAYS_ON")

        for p in self.prompts_dir.glob("*.md"):
            if p.name not in self.all_registered_files:
                errors.append(f"ORPHAN: {p.name} exists in prompts/ but is not registered")

        if errors:
            raise ValueError("; ".join(errors))

        return self

    # ── Methods ─────────────────────────────────────────────────────────────

    def prompt_path(self, filename: str) -> Path:
        """Absolute path to a prompt file."""
        return self.prompts_dir / filename

    def prompt_body(self, filename: str) -> str:
        """Read a prompt file and strip the header comment."""
        return _prompt_body_cached(self.prompts_dir, filename)

    def dest_name(self, mode_key: str, filename: str, ext: str = ".md") -> str:
        """Strip the mode prefix from a filename."""
        return _dest_name(mode_key, filename, ext)

    def validate_files(self) -> list[str]:
        """Check every registered filename exists in prompts/."""
        errors: list[str] = []

        for fname in self.all_registered_files:
            if not self.prompt_path(fname).exists():
                errors.append(f"MISSING: {fname}")

        for label, fname in self.concat_order:
            if fname not in self.all_registered_files:
                errors.append(f"CONCAT_ORDER '{label}': '{fname}' not in any mode or ALWAYS_ON")

        for p in self.prompts_dir.glob("*.md"):
            if p.name not in self.all_registered_files:
                errors.append(f"ORPHAN: {p.name} exists in prompts/ but is not registered")

        return errors

    # ── Ignore file generation ──────────────────────────────────────────────

    def generate_gitignore(self) -> str:
        """Generate .gitignore content from default patterns."""
        lines = [
            "# Auto-generated by prompt CLI — edit patterns in registry.py then rebuild",
            "# --- Dependencies ---",
        ]
        for p in self.default_ignore_patterns:
            if p in ["vendor/", "packages/"]:
                lines.append("")
                lines.append("# --- Build Outputs ---")
            if p in ["dist/", "build/", "*.egg-info/", "*.egg", "target/", "out/"]:
                continue  # Already handled
            if p in [".idea/", ".vscode/", "*.swp", "*.swo", "*~"]:
                lines.append("")
                lines.append("# --- IDE ---")
            if p in [".env", ".env.*", "*.pem", "*.key", "*.secret", "secrets/", "credentials/"]:
                lines.append("")
                lines.append("# --- Secrets ---")
            if p in ["*.log", "logs/"]:
                lines.append("")
                lines.append("# --- Logs ---")
            if p in [".DS_Store", "Thumbs.db"]:
                lines.append("")
                lines.append("# --- OS ---")
            lines.append(p)

        # Add build outputs section
        lines.append("")
        lines.append("# --- Build Outputs ---")
        for p in ["dist/", "build/", "*.egg-info/", "*.egg", "target/", "out/"]:
            lines.append(p)

        return "\n".join(lines) + "\n"

    def generate_clineignore(self) -> str:
        """Generate .clineignore content for Cline."""
        lines = [
            "# Auto-generated by prompt CLI — edit patterns in registry.py then rebuild",
            "# Files and directories to ignore in Cline",
            "",
        ]
        lines.extend(self.default_ignore_patterns)
        return "\n".join(lines) + "\n"

    def generate_cursorignore(self) -> str:
        """Generate .cursorignore content for Cursor."""
        lines = [
            "# Auto-generated by prompt CLI — edit patterns in registry.py then rebuild",
            "# Files and directories to ignore in Cursor",
            "",
        ]
        lines.extend(self.default_ignore_patterns)
        return "\n".join(lines) + "\n"

    def generate_kiloignore(self) -> str:
        """Generate .kiloignore content for Kilo Code."""
        lines = [
            "# Auto-generated by prompt CLI — edit patterns in registry.py then rebuild",
            "# Files and directories to ignore in Kilo Code",
            "",
        ]
        lines.extend(self.default_ignore_patterns)
        return "\n".join(lines) + "\n"

    def generate_copilotignore(self) -> str:
        """Generate .copilotignore content for GitHub Copilot."""
        lines = [
            "# Auto-generated by prompt CLI — edit patterns in registry.py then rebuild",
            "# Files and directories to ignore in GitHub Copilot",
            "",
        ]
        lines.extend(self.default_ignore_patterns)
        return "\n".join(lines) + "\n"


# ── Singleton instance ───────────────────────────────────────────────────────
# Yes - this is not a proper singleton - but it works for the current needs and
#       avoids hoop jumping from using pydantic
registry = Registry()
