# Claude Template Population Fix

**Status:** 🚧 IN PROGRESS — Phases 0–3a done (incl. macro consolidation); Phase 3b (core `general.md` fill-ins)
and Phase 4 (`validate`/concat) remain — both need a decision
**Date:** 2026-06-15
**Branch:** `fix/claude-template-population`
**Owner:** (unassigned)
**Related:** `../complete/TEMPLATE_SUBSTITUTION_FIX.md` (Kilo-only, ✅ done), `../complete/PRIMARY_AGENTS_LIST_FIX.md`, `SOURCE_CODE_UPDATES_DESIGN.md` (Part: "Dynamic Agent List")

## Progress

- ✅ **Phase 0** — regression test `tests/integration/test_claude_population.py` (single + multi-language; 5 tests, green).
- ✅ **Phase 1** — `convention_generator` now renders language + core conventions through Jinja2 with the per-folder
  **spec** as context (macro imports resolve; `{{ language }}`/`{{ package_manager }}`/`{{ linter }}`/`{{ formatter }}`
  and the `abstract_class_style` conditional blocks all populate). `prompt_builder` passes specs, not bare names.
  Result: **zero raw `{{`/`{%` left in any Claude output**, and each language gets its own spec.
- ✅ **Phase 2** — `ClaudeBuilder` now runs template-variable substitution on agent system prompts (composition with
  legacy `Builder`, mirroring the Kilo fix). `{{PRIMARY_AGENTS_LIST}}` is populated in the orchestrator agent.
- ✅ **Phase 3a — testing/coverage macros wired (the headline fix).** The convention templates' `### Testing`
  sections were literal stubs (`[Dynamic content - see template]`, `TODO`) and the imported testing/coverage macros
  were never called. Replaced the stub in all 7 convention files (python, typescript, golang, java, rust, kotlin,
  ruby) with `{{ testing.render_testing_section(language, test_framework, coverage_targets) }}` — consistent with the
  documented macro design (`prompts/macros/README.md`). **The user's test framework + coverage targets now render.**
  Exposed `coverage_targets` in the render context (the templates alias the coverage *macro module* as `coverage`).
  Removed 2 orphan `[Dynamic content]` placeholders in python.
- ✅ **Macro-directory consolidation (gap found & fixed).** There were TWO macro dirs: the canonical
  `prompts/macros/` (full) and a vestigial `agents/core/macros/` (1-line stubs). `CoreFilesLoader` (used by
  kilo/cline/cursor/copilot) resolved imports against the stub dir — so calling the real macros would have crashed
  those builders under StrictUndefined (the suite didn't cover that path). Repointed `CoreFilesLoader` at
  `prompts/macros/` and **deleted the stub `agents/core/macros/`**. The existing
  `test_conventions_conditional_rendering` loader was likewise repointed.
- Full suite: 1610 passed / 23 skipped; ruff + pyright clean. Verified all five builders build without crashing or
  leaking `{{`/`{%`/stub text.

---

## Problem

The **Claude** build path emits artifacts with **unrendered template variables and raw Jinja2**. Spec
choices a user makes during `prompticorn init` (language, runtime, package manager, test framework, linter,
formatter, coverage targets, abstract-class style) **never reach the generated Claude conventions**, and the
orchestrator agent ships a literal `{{PRIMARY_AGENTS_LIST}}`.

This was reproduced by building into a scratch dir for two scenarios (single-language Python; multi-language
monorepo = Python backend + TypeScript frontend) plus Kilo/Cline/Cursor/Copilot as controls.

### Why this happens (root cause)

Two parallel builder stacks exist:

| Stack | Used by | Has template substitution? |
|-------|---------|----------------------------|
| `builders/builder.py` (`Builder` + `TemplateHandlerRegistry` + `Jinja2TemplateRenderer`) | **Kilo** (via `KiloBuilder._builder`) | ✅ yes |
| `builders/base.py` (`Builder` ABC) → `ClaudeBuilder`, `convention_generator.py` | **Claude** | ❌ no |

`TEMPLATE_SUBSTITUTION_FIX.md` wired substitution into **KiloBuilder only** (composition: `self._builder =
Builder()`). `ClaudeBuilder` extends the `base.py` ABC and never calls `_substitute_template_variables`. The
convention generator reads files with plain `read_text()` and no Jinja rendering.

Net effect: the fix marked ✅ COMPLETE is **incomplete for every non-Kilo tool**, and the language-convention
rendering gap was never tracked anywhere.

---

## Confirmed bugs (with evidence)

### BUG 1 — Claude language conventions ship raw, unrendered Jinja2
`builders/convention_generator.py::generate_language_convention()` does `read_text()` only. Source files
(`agents/core/conventions-{lang}.md`) are full Jinja templates with macro imports.

Generated `.claude/conventions/languages/python.md` contains literally:
```
{%- import 'macros/naming_conventions.jinja2' as naming -%}
Language:             {{ language }} e.g., Python 3.11+
Package Manager:      {{ package_manager }} ...
{% if config.abstract_class_style == "abc" %}
```

### BUG 2 — Spec values never reach conventions (multi-language broken)
`prompt_builder.py` → `generate_all_conventions(languages)` passes only language **names**, not the per-folder
spec dicts. Proof: generated `python.md` is **byte-identical** between the single-Python build and the
multi-language build, despite different specs (uv/pytest/ruff/3.14 vs the TS spec). Even after BUG 1 is fixed,
there is no spec data to fill the variables with.

### BUG 3 — `{{PRIMARY_AGENTS_LIST}}` raw in Claude orchestrator
`.claude/agents/orchestrator-agent.md` contains literal `{{PRIMARY_AGENTS_LIST}}`. Kilo renders the full list
correctly — so the handler works; the Claude path just never invokes substitution.

### BUG 4 — Core `general.md` ships fill-in placeholders
`.claude/conventions/core/general.md` (from `agents/core/conventions.md`) contains `Repository type: TODO`,
`[LANG]`, `Database: TODO`, `Commit style: TODO`, `Target: TODO`. Repository type and language are known from
config; the rest are not captured anywhere. This is the first file Claude is told to load.

### BUG 5 (latent) — `registry.py` concat_order points at non-existent files
`registry.py::concat_order` references `agents/core/core-*.md` (e.g. `core-conventions-python.md`), but files
lack the `core-` prefix and `prompts_dir` only contains `macros/`. `build_concatenated_rules()` would emit
`## label — MISSING: filename`. Currently dead (Cline/Cursor/Copilot use the newer PromptBuilder path), but it
breaks `validate` and any future concat consumer.

---

## Plan

### Phase 0 — Lock in a regression test (do first)
- Add `tests/integration/test_claude_population.py` that builds Claude for (a) single Python and
  (b) multi-language Python+TypeScript, then asserts:
  - no output file contains `{{`, `{%`, `[LANG]`, or `MISSING:`;
  - `python.md` contains `pytest`/`ruff`/`uv` and `typescript.md` contains `vitest`/`eslint`/`pnpm`;
  - the two language conventions are **not** identical across differing specs;
  - `orchestrator-agent.md` contains real agent names, not `{{PRIMARY_AGENTS_LIST}}`.
- This test should fail today and pass when the phases below land.

### Phase 1 — Render language conventions with spec context (BUG 1 + BUG 2)
- Change `generate_language_convention()` and `generate_all_conventions()` to accept **spec dicts**, not just
  language names. Signature sketch: `generate_all_conventions(specs: list[dict] | dict | None)`.
- Render each convention through `Jinja2TemplateRenderer` (already supports macro imports from `prompts/macros`),
  passing the per-folder spec as context (`language`, `runtime`, `package_manager`, `linter`, `linters`,
  `formatter`, `abstract_class_style`, `coverage`, plus `config` for the `{% if config.abstract_class_style %}`
  blocks).
- Multi-language: render one convention per folder spec keyed by language. Decide behavior when two folders use
  the same language with different specs (recommend: emit per-folder filename, e.g.
  `languages/python-backend.md`, or merge with a documented precedence — needs a decision, see Open Questions).
- Update `prompt_builder.py:313-321` to pass the full spec list from config instead of `_extract_all_languages_from_config`.

### Phase 2 — Run template substitution in the Claude path (BUG 3)
- Mirror the Kilo fix via composition: give `ClaudeBuilder` a `Builder()` (from `builders/builder.py`) instance
  and call `_substitute_template_variables(system_prompt, config)` in `_render_agent_file` before rendering.
- Alternatively (preferred long-term per `TEMPLATE_SUBSTITUTION_FIX.md` "Future Improvements"): extract
  `substitute_template_variables()` into `builders/template_utils.py` and call from both Kilo and Claude to
  avoid coupling to the legacy `Builder`.
- Confirm `PrimaryAgentsHandler` respects persona filtering (currently lists all registry agents even when
  personas exclude some — see Minor below).

### Phase 3 — Convention template content (the user's headline concern) ⏳ NEXT
The wiring is fixed, but the **convention templates don't reference the values**:
- **Test framework / coverage not shown.** `conventions-{lang}.md` has a `### Testing` section that is literal
  stub text (`[Dynamic content - see template]`, `TODO`) and imports `macros/testing_sections.jinja2` +
  `macros/coverage_targets.jinja2` **without ever calling them**. Replace the stubs with macro calls
  (`{{ testing.* (test_framework, ...) }}`, `{{ coverage.* (coverage) }}`) and/or add a `Test Framework:
  {{ test_framework }}` header line mirroring the existing Linter/Formatter lines. Spans ~20 language files —
  needs the macro signatures pinned down first.
- **Core `general.md` fill-ins (BUG 4).** `conventions.md` carries `Repository type: TODO`, `[LANG]`,
  `Database: TODO`, `Commit style: TODO`, `Target: TODO`. For values known from config (repository type, primary
  language) substitute during `generate_core_convention()` (now spec-aware-capable). For uncaptured values
  (Database, ORM, Deploy): either add to the `init` questionnaire + spec, or make the fill-in intent obvious
  (e.g. `<FILL IN: database>`) rather than a bare `TODO`. Needs a decision (see Open Questions).
- Tighten the regression test to assert `test_framework`/coverage values appear once the templates reference them.

### Phase 4 — `validate` / concat_order (BUG 5) ⏳ NEEDS DECISION
**Diagnosis (answers "broken because we moved on, or just broken?"): broken because the design moved on.** The
project migrated from a flat `prompts/` dir (with `core-`prefixed files + flat-concatenation output) to
`agents/`-based IR discovery (`Registry.from_discovery`). The legacy `prompticorn/registry.py` (`prompts_dir`,
`mode_files`, `always_on`, `concat_order`) and `build_concatenated_rules()` were never updated:
- `build_concatenated_rules()` / `concat_order` (output side) = **fully dead** (zero callers anywhere).
- **`prompticorn validate` is LIVE and BROKEN** — it calls `registry.validate_files()` which checks the stale
  registry against `prompts_dir` (now only `macros/`), reporting **47 false MISSING/ORPHAN errors**.

Recommended (consistent with current design): **retire** the dead flat-concat machinery
(`build_concatenated_rules`, `concat_order`) and **repoint `validate`** at the live `agents/` IR registry
(`Registry.from_discovery`) — or remove `validate` if redundant. Keep the legacy `Builder` class itself (still used
for `_substitute_template_variables` by Kilo + Claude). Update `tests/unit/test_registry_comprehensive.py`.

---

## Verification
- Phase 0 regression test passes.
- Manual: `uv run` build of both scenarios into a scratch dir; `grep -rn '{{\|{%\|\[LANG\]\|MISSING:'` returns
  nothing across `.claude/`.
- `pytest` green; `prompticorn validate` clean.

## Risks
- **Macro resolution**: conventions import `macros/*.jinja2`; the renderer's registry loader must resolve those
  paths. Verify against `prompts/macros/` (exists) early in Phase 1.
- **Multi-language collision**: same language in two folders needs a defined output strategy (Open Question).
- **Coupling**: reusing legacy `Builder` in Claude re-introduces the coupling `TEMPLATE_SUBSTITUTION_FIX.md`
  tried to avoid — prefer the `template_utils.py` extraction.

## Open questions (need a decision before/while implementing)
1. Multi-language same-language folders → per-folder convention files, or merge with precedence?
2. Core-convention `TODO`s for uncaptured fields → add to `init` questionnaire, or keep as explicit fill-ins?
3. concat_order → repair or delete?

## Minor / follow-ups
- `PRIMARY_AGENTS_LIST` ignores persona filtering (lists all registry agents).
- Cline/Cursor/Copilot emit **no** conventions at all, so language/test-framework choices never appear in their
  output — confirm whether by design (they lean on `AGENTS.md`).
