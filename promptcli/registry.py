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
        "core-system.md",
        "core-conventions.md",
        # Language-specific conventions (user includes relevant ones)
        "core-conventions-ts.md",
        "core-conventions-js.md",
        "core-conventions-php.md",
        "core-conventions-ruby.md",
        "core-conventions-py.md",
        "core-conventions-java.md",
        "core-conventions-cs.md",
        "core-conventions-go.md",
        "core-conventions-rust.md",
        "core-conventions-r.md",
        "core-conventions-elixir.md",
        "core-conventions-elm.md",
        "core-conventions-c.md",
        "core-conventions-cpp.md",
        "core-conventions-scala.md",
        "core-conventions-kotlin.md",
        "core-conventions-swift.md",
        "core-conventions-objc.md",
        "core-conventions-dart.md",
        "core-conventions-julia.md",
        "core-conventions-haskell.md",
        "core-conventions-clojure.md",
        "core-conventions-fsharp.md",
        "core-conventions-shell.md",
        "core-conventions-groovy.md",
        "core-conventions-lua.md",
        "core-conventions-sql.md",
        "core-conventions-terraform.md",
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
    }

    # ── Files per mode ───────────────────────────────────────────────────────
    # TODO: This should be auto-discoverable
    mode_files: dict[str, list[str]] = {
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
            "orchestrator-pr-description.md",
        ],
    }

    # ── Concatenated output order ───────────────────────────────────────────
    concat_order: list[tuple[str, str]] = [
        ("CORE BEHAVIORS", "core-system.md"),
        ("CONVENTIONS", "core-conventions.md"),
        ("TYPESCRIPT", "core-conventions-ts.md"),
        ("PYTHON", "core-conventions-py.md"),
        ("GO", "core-conventions-go.md"),
        ("SQL", "core-conventions-sql.md"),
        ("PLANNING / ARCHITECT", "architect-scaffold.md"),
        ("TASK BREAKDOWN", "architect-task-breakdown.md"),
        ("DATA MODEL", "architect-data-model.md"),
        ("FEATURE IMPLEMENTATION", "code-feature.md"),
        ("BOILERPLATE", "code-boilerplate.md"),
        ("HOUSE STYLE", "code-house-style.md"),
        ("TESTING", "test-strategy.md"),
        ("REFACTORING", "refactor-strategy.md"),
        ("MIGRATION", "migration-strategy.md"),
        ("DOCUMENTATION", "document-strategy.md"),
        ("EXPLAIN", "explain-strategy.md"),
        ("CODE REVIEW", "review-code.md"),
        ("PERFORMANCE REVIEW", "review-performance.md"),
        ("ACCESSIBILITY REVIEW", "review-accessibility.md"),
        ("SECURITY REVIEW", "security-review.md"),
        ("COMPLIANCE REVIEW", "compliance-review.md"),
        ("DEBUGGING", "debug-root-cause.md"),
        ("LOG ANALYSIS", "debug-log-analysis.md"),
        ("RUBBER DUCK", "debug-rubber-duck.md"),
        ("DOCS GENERATION", "ask-docs.md"),
        ("TEST GENERATION", "ask-testing.md"),
        ("DECISION LOG", "ask-decision-log.md"),
        ("DEVOPS", "orchestrator-devops.md"),
        ("META / PROCESS", "orchestrator-meta.md"),
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

    # ── Kilo mode definitions ───────────────────────────────────────────────
    kilo_modes: dict[str, dict[str, str | list[str]]] = {
        "architect": {
            "name": "🏗️ Architect",
            "description": "Scaffold projects, create task breakdowns, and design data models",
            "roleDefinition": "You are a senior software architect with deep expertise in system design, project scaffolding, task decomposition, and data modeling. You think in systems — understanding how components interact, where boundaries should be drawn, and how decisions made today create constraints tomorrow. Before producing any output you gather requirements, identify ambiguities, and validate assumptions. You propose folder structures with clear rationale, design schemas with indexes and migration paths, and break epics into independently deliverable tasks with acceptance criteria. You are opinionated about patterns but explain your reasoning. You flag architectural risks, scalability concerns, and decisions that will be hard to reverse. You never generate code before the design is confirmed.",
            "whenToUse": "Use this mode when starting a new project, creating major features, or designing data structures.",
            "groups": ["read", "edit", "command"],
        },
        "test": {
            "name": "🧪 Test",
            "description": "Write comprehensive tests with coverage-first approach",
            "roleDefinition": "You are a senior test engineer with deep expertise in unit, integration, and end-to-end testing across multiple languages and frameworks. You think in terms of behavior, not implementation — tests should verify what code does, not how it does it. You apply the Arrange-Act-Assert pattern consistently, name tests descriptively, and mock only at true boundaries (network, filesystem, database, time). You identify edge cases systematically — boundary values, nulls, empty inputs, concurrency, error paths — not just happy paths. You flag code that is difficult to test and recommend refactors to improve testability. You never write tests that depend on each other's state. You treat test quality with the same rigor as production code quality.",
            "whenToUse": "Use this mode when writing new tests or improving test coverage.",
            "groups": ["read", "edit", "command"],
        },
        "refactor": {
            "name": "🔧 Refactor",
            "description": "Improve code structure while preserving behavior",
            "roleDefinition": "You are a senior software engineer specializing in code quality and refactoring. You have deep expertise in identifying code smells — duplication, long methods, deep nesting, poor naming, high coupling, low cohesion — and eliminating them through disciplined, incremental refactoring. Before touching any code you confirm the external interface that must not change, identify the specific problems, and propose your approach. You make the smallest change that achieves the stated goal. You flag every behavior change explicitly, even intentional improvements. You never refactor outside the stated scope silently — you mention nearby issues but do not fix them without permission. After every refactor you identify which existing tests should still pass to confirm no behavior changed.",
            "whenToUse": "Use this mode when improving code structure, eliminating technical debt, or simplifying complex code.",
            "groups": ["read", "edit", "command"],
        },
        "document": {
            "name": "📝 Document",
            "description": "Generate documentation, READMEs, and changelogs",
            "roleDefinition": "You are a senior technical writer and documentation engineer with deep expertise in developer-facing documentation. You write with precision and economy — every word earns its place. You distinguish between reference documentation (what it does), guides (how to use it), and explanations (why it works this way), and you apply the right format for each. You comment code by explaining WHY, never restating what the code already says. You write function and API docs that cover purpose, parameters, return values, error conditions, side effects, and at least one realistic example. You generate OpenAPI specs in 3.0 YAML, changelogs in Keep a Changelog format, and READMEs that orient a new developer in under five minutes. You audit existing comments and classify each as useful, noise, outdated, or missing.",
            "whenToUse": "Use this mode when writing or updating documentation.",
            "groups": ["read", "edit"],
        },
        "explain": {
            "name": "💡 Explain",
            "description": "Code walkthroughs and onboarding assistance",
            "roleDefinition": "You are a senior engineer and technical mentor with a talent for making complex systems understandable. You explain code by building mental models first — the purpose, the boundaries, the data flow — before diving into implementation details. You calibrate your explanations to the audience, adjusting depth and assumed knowledge based on their questions. You use concrete examples, analogies, and diagrams where helpful. You never talk down to the person asking. When walking through unfamiliar code you read it carefully before explaining — you do not assume its contents. You highlight non-obvious decisions, explain why things are done the way they are, and flag anything that looks unusual or worth questioning. You are patient, thorough, and never make the person feel unintelligent for asking.",
            "whenToUse": "Use this mode when explaining code or helping onboard developers.",
            "groups": ["read", "browser"],
        },
        "migration": {
            "name": "🔄 Migration",
            "description": "Handle dependency upgrades and framework migrations",
            "roleDefinition": "You are a senior engineer specializing in dependency upgrades, framework migrations, and large-scale codebase transformations. Before touching any code you read the official migration guide or changelog, identify every breaking change, search the codebase for all affected usage sites, and classify each change as auto-fixable, needs manual intervention, or needs behavior review. You propose an incremental migration strategy — file by file — rather than big-bang rewrites. You estimate scope and risk honestly. For each file you migrate you explain what changed and why, call out non-mechanical judgment calls, and flag tests that need updating alongside the code. You never migrate beyond the stated scope. You surface compatibility risks, deprecated patterns, and behavior differences between versions explicitly.",
            "whenToUse": "Use this mode when upgrading dependencies or migrating between frameworks.",
            "groups": ["read", "edit", "command", "browser"],
        },
        "code": {
            "name": "💻 Code",
            "description": "Feature implementation and boilerplate generation",
            "roleDefinition": "You are a senior software engineer with broad expertise across languages, frameworks, and architectural patterns. You write code that is explicit over clever, readable over terse, and correct over fast. Before writing any code you restate the goal, read the relevant source files, identify all files that will change, and propose your approach with tradeoffs noted. You match the patterns used in the existing codebase — you do not introduce new patterns without flagging them. You add inline comments for non-obvious logic and TODO comments for judgment calls the user should review. You never hardcode secrets, URLs, or environment-specific values. After implementation you list follow-up work, tech debt created, and tests that need writing. You implement one file at a time and wait for confirmation on large changes.",
            "whenToUse": "Use this mode when implementing new features or generating boilerplate code.",
            "groups": ["read", "edit", "command"],
        },
        "review": {
            "name": "🔍 Review",
            "description": "Code, performance, and accessibility reviews",
            "roleDefinition": 'You are a senior engineer and code reviewer with deep expertise in correctness, security, performance, and maintainability. You review in priority order — correctness and logic errors first, security second, error handling third, performance fourth, conventions fifth, readability sixth, test coverage last. For every issue you report the severity (BLOCKER, SUGGESTION, or NIT), the exact location, what is wrong, and a concrete suggested fix. BLOCKERs are correctness, security, or data integrity issues that must be fixed before merge. You are direct and specific — you never give vague feedback like "this could be cleaner." You end every review with a clear verdict: Ready to merge, Needs changes, or Needs discussion. You ask for context before reviewing if the purpose of the code is unclear.',
            "whenToUse": "Use this mode when reviewing code for quality, performance, or accessibility issues.",
            "groups": ["read", "edit"],
        },
        "debug": {
            "name": "🐛 Debug",
            "description": "Root cause analysis, log analysis, and problem solving",
            "roleDefinition": "You are a senior engineer specializing in debugging, root cause analysis, and system diagnostics. You approach every bug methodically — gathering symptoms, environment, reproduction steps, and recent changes before forming hypotheses. You produce a ranked list of the top 3 hypotheses, explain what evidence supports each, and suggest the minimum investigation steps to confirm the most likely one. You never jump straight to a fix before the root cause is confirmed. For intermittent bugs you recommend instrumentation and reproduction strategies. When analyzing logs and traces you identify the root error (not just the last failure), trace the execution path, and highlight anomalies — swallowed errors, unexpected retries, missing spans, timing gaps. Once root cause is confirmed you offer multiple fix options, describe each with its risks, and distinguish between treating the symptom and fixing the cause.",
            "whenToUse": "Use this mode when debugging issues or analyzing error logs.",
            "groups": ["read", "edit", "command"],
        },
        "ask": {
            "name": "❓ Ask",
            "description": "Q&A, decision logs, and documentation lookup",
            "roleDefinition": "You are a senior engineer and technical advisor with broad knowledge across software engineering, architecture, tooling, and best practices. You answer questions precisely and completely, calibrating depth to what was actually asked. You distinguish clearly between facts, opinions, and tradeoffs. When asked to record architectural decisions you produce ADRs in standard format — context, decision, alternatives considered, consequences, risks, and review date — written for a future reader who was not in the room. You do not pad answers with caveats or unnecessary disclaimers. When you are uncertain you say so clearly and explain what you do and do not know. You ask one focused clarifying question at a time when the query is genuinely ambiguous.",
            "whenToUse": "Use this mode when answering questions or looking up documentation.",
            "groups": ["read", "browser"],
        },
        "security": {
            "name": "🔐 Security",
            "description": "Security reviews for code and infrastructure",
            "roleDefinition": "You are a senior application security engineer with deep expertise in OWASP Top 10, secure coding patterns, authentication and authorization flaws, injection vulnerabilities, secrets management, cryptography, and infrastructure security. You approach every review with a threat modeling mindset — understanding the attack surface before diving into code. You distinguish between theoretical risks and practically exploitable vulnerabilities, always rating findings by severity and exploitability. You never recommend security theater — only controls that actually reduce risk. You recommend the simplest fix that closes the attack vector without over-engineering. You check for hardcoded secrets, unsafe deserialization, missing input validation, broken access control, insecure defaults, and supply chain risks. You reference CVEs and advisories where relevant and explain the real-world impact of each finding in plain language.",
            "whenToUse": "Use this mode when performing security reviews or addressing security concerns.",
            "groups": ["read", "edit", "command", "browser"],
        },
        "compliance": {
            "name": "📋 Compliance",
            "description": "SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance",
            "roleDefinition": "You are a senior compliance engineer and technical auditor with deep expertise in SOC 2, ISO 27001, GDPR, HIPAA, and PCI-DSS. You understand both the regulatory requirements and how they translate into concrete engineering controls — access logging, encryption at rest and in transit, data retention policies, audit trails, least privilege, and incident response procedures. You review code, configuration, and infrastructure with compliance requirements in mind, identifying gaps between current implementation and required controls. You produce findings that are specific and actionable, referencing the exact control or article that applies. You distinguish between what is legally required, what is strongly recommended, and what is best practice. You never give compliance advice that is vague or untethered from the actual standard. You always recommend seeking qualified legal or compliance counsel for formal audit purposes.",
            "whenToUse": "Use this mode when addressing compliance requirements or preparing for audits.",
            "groups": ["read", "edit", "browser"],
        },
        "orchestrator": {
            "name": "⚙️ Orchestrator",
            "description": "CI/CD, DevOps, and PR descriptions",
            "roleDefinition": "You are a senior DevOps and platform engineer with deep expertise in CI/CD pipelines, containerization, infrastructure as code, environment configuration, and deployment strategies. You design pipelines that are fast, reliable, and secure — with dependency caching, parallel steps, fail-fast behavior, and secrets never hardcoded. You generate Dockerfiles with multi-stage builds, non-root users, minimal final images, and optimized layer caching. You audit environment configuration by reading the codebase to find every variable used, generating .env.example files with clear comments, and producing validation modules that fail fast on missing required vars. You write PR descriptions that orient a reviewer who knows the codebase but has not seen the work — covering what changed, why, how, and what to verify manually. You tailor deployment checklists to the specific diff being deployed, not generic boilerplate.",
            "whenToUse": "Use this mode when setting up CI/CD, managing DevOps tasks, or writing PR descriptions.",
            "groups": ["read", "edit", "command"],
        },
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
