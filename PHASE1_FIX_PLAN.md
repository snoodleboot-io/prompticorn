# Phase 1 Implementation: Fix Plan with Detailed Checklist

## Current Status
- Code written: ✓ (KiloIDEBuilder refactored, tests created)
- Code tested: ✓ (17 unit tests pass)
- Code verified: ✗ (No actual output validation against Kilo spec)
- Code validated: ✗ (No end-to-end testing)

## Issues Identified

### Critical Issues (Blocks Phase 1 completion)

**Issue #1: YAML Frontmatter Formatting Bug**
- Location: `_build_frontmatter()` method, line 448
- Problem: Missing newline before closing `---`
- Current: `f"---\n{yaml_str}---"`
- Should be: `f"---\n{yaml_str}\n---"`
- Impact: YAML may fail to parse; closing marker should be on own line
- Severity: **CRITICAL** - blocks file validation

**Issue #2: Regex-to-Glob Conversion is Too Simplistic**
- Location: `_regex_to_glob()` method, lines 367-418
- Problem: Complex regex patterns with alternation and escaping may convert incorrectly
- Example input: `"(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)"`
- Expected output: Something like `docs/**/*.md` OR `.promptosaurus/sessions/**/*.md`
- Current approach: Takes first alternative, may lose patterns
- Impact: Generated file permissions may be wrong
- Severity: **HIGH** - affects permission correctness

**Issue #3: Browser Access Ignored**
- Location: `_map_groups_to_permissions()` method, lines 338-340
- Problem: "browser" group type is silently ignored
- Current: `elif group_entry == "browser": pass`
- Impact: Browser access permission lost in translation
- Severity: **MEDIUM** - affects feature completeness

**Issue #4: No Output Validation**
- Location: Integration testing
- Problem: Tests pass but don't validate generated file format
- Impact: Can't know if output is valid Kilo format
- Severity: **CRITICAL** - blocks end-to-end verification

**Issue #5: No End-to-End Testing**
- Location: Integration testing
- Problem: Never run `promptosaurus init` to generate and inspect actual files
- Impact: Can't verify Kilo IDE can read the generated files
- Severity: **CRITICAL** - blocks Phase 1 completion

---

## Fix Plan (Phased Approach)

### Phase 1A: Fix Critical Code Bugs (2-4 hours)

**Checklist:**

- [ ] **Fix YAML frontmatter closing**
  - [ ] Open `promptosaurus/builders/kilo/kilo_ide.py`
  - [ ] Go to line 448 in `_build_frontmatter()`
  - [ ] Change: `return f"---\n{yaml_str}---"`
  - [ ] To: `return f"---\n{yaml_str}\n---"`
  - [ ] Verify: closing `---` is on its own line

- [ ] **Fix regex-to-glob conversion**
  - [ ] Analyze the actual regex patterns in `.kilocodemodes`:
    - [ ] `"(docs/.*\\.md$|...)"` - alternation with escaped dots
    - [ ] Check how many agents use complex patterns
  - [ ] Option A: Use `fnmatch` or `glob2` library to convert
    - [ ] Pros: Robust, tested library
    - [ ] Cons: May need to add dependency
  - [ ] Option B: Use regex as-is in permission object
    - [ ] Pros: No conversion needed
    - [ ] Cons: Not as readable
  - [ ] Decision: Recommend **Option B** (use regex directly) for MVP
  - [ ] Change: Store regex patterns as-is instead of converting
  - [ ] Update: `_map_groups_to_permissions()` to skip `_regex_to_glob()`

- [ ] **Handle browser access**
  - [ ] Research: Does Kilo have a "browser" permission type?
    - [ ] Check Kilo docs for webfetch, websearch, browser access
  - [ ] Options:
    - [ ] Option A: Map "browser" to `"webfetch": "allow"`
    - [ ] Option B: Map "browser" to multiple tools: webfetch, websearch
    - [ ] Option C: Ignore for MVP, document as limitation
  - [ ] Decision: Recommend **Option C** for MVP
  - [ ] Update: Add comment in code explaining limitation

- [ ] **Add validation function**
  - [ ] Create `_validate_agent_file()` method
  - [ ] Check: YAML frontmatter parses correctly
  - [ ] Check: Required fields present (description, mode, permission)
  - [ ] Check: Permission object has valid structure
  - [ ] Log: Warnings for missing optional fields
  - [ ] Return: True/False validation status

- [ ] **Add verbose logging to builder**
  - [ ] Log each agent file being created
  - [ ] Log permission structure for debugging
  - [ ] Log any conversion issues (regex→glob)

### Phase 1B: Add Validation Testing (2-3 hours)

**Checklist:**

- [ ] **Create output validation test**
  - [ ] New test: `test_kilo_ide_builder_validates_yaml_format()`
  - [ ] Build output to temp directory
  - [ ] Load generated `.md` file
  - [ ] Parse YAML frontmatter
  - [ ] Verify required fields
  - [ ] Assert YAML is valid

- [ ] **Create permission structure test**
  - [ ] New test: `test_permission_object_structure()`
  - [ ] Verify permission object has correct nesting
  - [ ] Verify wildcard denies work
  - [ ] Verify file patterns are present

- [ ] **Create end-to-end test**
  - [ ] New test: `test_kilo_ide_builder_end_to_end()`
  - [ ] Run full build with actual config
  - [ ] Check all 13 agents created
  - [ ] Check all files are readable and valid YAML
  - [ ] Check permission structures are complete
  - [ ] Create a snapshot of one agent file for manual review

- [ ] **Add snapshot test**
  - [ ] Save example output (architect.md) to test fixtures
  - [ ] Use for regression testing in future
  - [ ] Helps spot format changes

### Phase 1C: Manual Verification (1-2 hours)

**Checklist:**

- [ ] **Run builder manually**
  - [ ] Create test directory: `/tmp/promptosaurus-test/`
  - [ ] Copy `.promptosaurus.yaml` to test dir
  - [ ] Run: `cd /tmp/promptosaurus-test && uv run python3 -c "from promptosaurus.builders.kilo.kilo_ide import KiloIDEBuilder; builder = KiloIDEBuilder(); builder.build(Path('.'), config=config, dry_run=False)"`
  - [ ] Check: `.kilo/agents/` directory created
  - [ ] Check: All 13 agent files present

- [ ] **Inspect generated files**
  - [ ] Pick 3 agents: architect, test, review
  - [ ] For each:
    - [ ] Open file: `.kilo/agents/{agent}.md`
    - [ ] Check: YAML frontmatter is valid (starts `---`, ends `---`)
    - [ ] Check: Fields present: description, mode, permission, color
    - [ ] Check: Permission object is properly nested (not array)
    - [ ] Check: Markdown body contains roleDefinition
    - [ ] Verify: No obvious formatting issues

- [ ] **Validate YAML syntax**
  - [ ] Create validation script
  - [ ] For each `.md` file:
    - [ ] Read file
    - [ ] Extract YAML frontmatter (between `---` markers)
    - [ ] Parse with `yaml.safe_load()`
    - [ ] Verify all required fields present
    - [ ] Log any parsing errors

- [ ] **Check file count**
  - [ ] Count agents in `.kilocodemodes`: should be 13
  - [ ] Count files in `.kilo/agents/`: should be 13
  - [ ] Compare: all agents have corresponding files

- [ ] **Permission spot-check**
  - [ ] Architect agent should have:
    - [ ] `read: {*: allow}`
    - [ ] `edit: {docs/**/*.md: allow, ...}`
  - [ ] Test agent should have:
    - [ ] `read: {*: allow}`
    - [ ] `edit: {*: allow}`
    - [ ] `bash: allow`

### Phase 1D: Documentation & Sign-Off (1 hour)

**Checklist:**

- [ ] **Update PHASE1_COMPLETION_SUMMARY.md**
  - [ ] Mark issues as FIXED
  - [ ] Document regex-to-glob decision (use regex as-is)
  - [ ] Document browser access decision (ignored for MVP)
  - [ ] Add validation test results

- [ ] **Create implementation notes**
  - [ ] Document why regex patterns stored as-is
  - [ ] Document format decision rationale
  - [ ] Note Kilo IDE version compatibility

- [ ] **Commit all changes**
  - [ ] Fix commit: "fix(kilo-builder): correct YAML frontmatter and permission handling"
  - [ ] Test commit: "test(kilo-builder): add validation and end-to-end tests"
  - [ ] Update commit: "docs: update Phase 1 completion summary with fixes"

---

## Success Criteria

Phase 1 is **COMPLETE** when:

- [x] Code compiles without syntax errors ✓
- [ ] Unit tests pass (17/17) ✓ (will still pass)
- [ ] YAML frontmatter is valid and parseable
- [ ] Permission objects are correctly structured
- [ ] All 13 agents generate without errors
- [ ] Regex patterns are handled correctly
- [ ] Output files can be manually inspected and verified
- [ ] No critical YAML formatting issues
- [ ] Documentation updated with actual findings
- [ ] Issues documented for Phase 2

---

## Timeline Estimate

- **Phase 1A (Fixes):** 2-4 hours
- **Phase 1B (Testing):** 2-3 hours  
- **Phase 1C (Verification):** 1-2 hours
- **Phase 1D (Documentation):** 1 hour
- **Total: 6-10 hours**

---

## Known Limitations (For Phase 2)

- Browser access handling deferred
- Optional agent fields (model, steps, temperature) not supported yet
- No migration from old .kilocodemodes format
- Regex patterns used as-is (may not be ideal for all cases)
- No support for agent variants or hidden agents

---

## Rollback Plan

If during verification we discover the output is fundamentally incompatible with Kilo:

1. Revert all Phase 1 code changes to main branch
2. Go back to pure planning/design phase
3. Create new design incorporating actual Kilo format requirements
4. Implement with proper validation from start

Currently, this is unlikely given the format appears sound, just needs fixes.

