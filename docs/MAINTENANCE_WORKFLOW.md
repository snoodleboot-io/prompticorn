# Documentation Maintenance Workflow

**Version:** 1.0  
**Last Updated:** April 11, 2026  
**Status:** Active  
**Owner:** Engineering Team

---

## Overview

This document describes the ongoing procedures for maintaining Promptosaurus documentation quality, currency, and discoverability. It covers:

1. **Validation procedures** - Automated checks for content quality
2. **Update procedures** - How to keep docs in sync with code
3. **Quality metrics** - Tracking documentation health
4. **Review process** - Ensuring docs stay accurate
5. **Tool support** - Scripts and automation

---

## 1. Documentation Validation Framework

### 1.1 Automated Checks (Weekly)

Every Monday at 0:00 UTC, run comprehensive documentation validation:

```bash
# Run validation suite
cd promptosaurus
python validation/run_validation.py --check all

# Generates validation reports:
# - validation/link-check-report.txt
# - validation/content-validation-report.txt
# - validation/schema-validation-report.txt
# - validation/coverage-report.txt
```

#### Check 1: Link Validation

**What it checks:**
- All markdown links are valid
- No broken internal references
- All cross-document links working
- URLs are accessible

**Script:**
```bash
python -c "
import os
import re
from pathlib import Path

docs_path = Path('docs')
broken_links = []

for md_file in docs_path.rglob('*.md'):
    with open(md_file) as f:
        content = f.read()
        # Extract [text](link) patterns
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, link in links:
            # Skip external URLs
            if link.startswith('http'):
                continue
            # Check internal links
            if link.startswith('#'):
                continue
            target = (md_file.parent / link).resolve()
            if not target.exists():
                broken_links.append((md_file, link))

if broken_links:
    print('BROKEN LINKS FOUND:')
    for file, link in broken_links:
        print(f'  {file}: {link}')
else:
    print('✅ All links valid')
"
```

#### Check 2: Content Validation

**What it checks:**
- Agent files have required sections
- Workflow files have required sections
- Skill files have required sections
- All files have frontmatter where required

**Required Sections by Type:**

**Agent Files** (prompt.md):
```
✅ Role/Purpose (first 2-3 sentences)
✅ Key Responsibilities (bullet list)
✅ Expertise Areas (bullet list)
✅ Interaction Style (how to work with agent)
✅ Related Agents (links to complementary agents)
```

**Workflow Files** (workflow.md):
```
✅ Title/Purpose (clear description)
✅ When to Use (scenarios)
✅ Prerequisites (setup needed)
✅ Steps (numbered task list)
✅ Common Issues (troubleshooting)
✅ Examples (real-world scenario)
✅ Related Resources (links)
```

**Skill Files** (skill.md):
```
✅ Title/Name (what skill teaches)
✅ Overview (brief explanation)
✅ When It Matters (context)
✅ Key Concepts (main ideas)
✅ Practical Example (code or scenario)
✅ Best Practices (dos/don'ts)
✅ Related Skills (links)
```

**Implementation:**
```python
# validation/content_validator.py
def validate_agent_file(file_path: Path) -> list[str]:
    """Validate agent prompt.md has required sections."""
    with open(file_path) as f:
        content = f.read()
    
    required = [
        'Role', 'Responsibilities', 'Expertise',
        'Interaction', 'Related Agents'
    ]
    missing = []
    for section in required:
        if section.lower() not in content.lower():
            missing.append(section)
    return missing
```

#### Check 3: Schema Validation

**What it checks:**
- File structure matches expected patterns
- Directory organization is correct
- Naming conventions followed
- No orphaned or undocumented files

**Schema Rules:**
```
agents/
├── [agent-name]/
│   ├── prompt.md  ← Agent instruction
│   └── subagents/
│       └── [subagent-name]/
│           ├── minimal/
│           │   └── prompt.md
│           └── verbose/
│               └── prompt.md

workflows/
├── [workflow-name]/
│   ├── minimal/
│   │   └── workflow.md
│   └── verbose/
│       └── workflow.md

skills/
├── [skill-name]/
│   ├── minimal/
│   │   └── skill.md
│   └── verbose/
│       └── skill.md
```

### 1.2 Manual Review (Bi-weekly)

Every other Wednesday, conduct manual documentation review:

**Checklist:**
- [ ] Read 3-5 random agent instructions (check for clarity)
- [ ] Check 5 workflows (verify steps are actionable)
- [ ] Review 5 skills (ensure examples work)
- [ ] Sample cross-references (do links lead where expected?)
- [ ] Check QUICKSTART & PERSONA_GUIDES (still accurate?)
- [ ] Review INDEX.md (navigation still makes sense?)

**Process:**
1. Pick random docs (use random selection tool)
2. Read each one carefully
3. Look for: clarity, accuracy, completeness
4. File issues if problems found
5. Update docs if minor fixes needed

**Time Required:** ~2 hours

---

## 2. Update Procedures

### 2.1 When Code Changes, Update Docs

**Trigger:** Every code commit that affects agents/workflows/builders

**Procedure:**

1. **Agent changes** → Update `promptosaurus/agents/[agent]/prompt.md`
   - If responsibility changed: update "Key Responsibilities" section
   - If new subagent: create new subagent directory
   - If expertise changed: update "Expertise Areas" section

2. **Workflow changes** → Update workflow files
   - If process changed: update "Steps" section
   - If tools changed: update "Prerequisites"
   - If new common issue: add to "Common Issues"

3. **Builder changes** → Update builder documentation
   - If new builder added: create builder guide in `docs/builders/`
   - If builder behavior changed: update guide

**Example:**

```markdown
# Before (git diff)
Agent Role: DevOps Engineer
Responsibilities:
- Infrastructure management
- Deployment automation

# After (updated prompt.md)
Agent Role: DevOps Engineer + SRE
Responsibilities:
- Infrastructure management
- Deployment automation
- On-call incident response  ← NEW
- Production monitoring      ← NEW
```

### 2.2 Documentation Update Checklist

When updating docs, verify:

- [ ] File saved in correct location
- [ ] Naming convention followed (snake_case/kebab-case)
- [ ] Related documentation updated (if cross-references)
- [ ] LIBRARY_INDEX.md updated if new items
- [ ] Links still valid
- [ ] Formatting consistent with existing docs
- [ ] All examples still accurate
- [ ] Tests updated if relevant

### 2.3 When Tests Change, Update Test Docs

**Trigger:** New test file or test suite changes

**Procedure:**

1. Ensure test file has comprehensive docstrings
2. Add example test cases as documentation
3. Update test coverage report: `_temp/validation/COVERAGE_REPORT.validation.md`

---

## 3. Quality Metrics & Tracking

### 3.1 Documentation Health Dashboard

Track these metrics monthly (update QUALITY_METRICS.md):

```
Documentation Completeness:     [TARGET: 100%]
  - Agents with full docs:      9/9  (100%)
  - Workflows with docs:        49/49 (100%)
  - Skills with docs:           58/58 (100%)
  - Builders documented:        5/5  (100%)

Link Quality:                   [TARGET: 100%]
  - Valid internal links:       [automated check]
  - Broken links:               0
  - External link health:       [weekly scan]

Content Quality:                [TARGET: >95%]
  - Sections complete:          [automated check]
  - Grammar/spelling:           [spell check]
  - Outdated content:           [quarterly review]

Usage:                          [INFORMATIONAL]
  - Downloads:                  [tracked]
  - Documentation views:        [tracked]
  - Search queries:             [tracked]
```

**Update Procedure:**

```bash
# Run monthly (1st of month)
python validation/run_validation.py --metrics

# Updates docs/QUALITY_METRICS.md automatically
# Generates graphs for trends over time
```

### 3.2 Metric Thresholds

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Doc Completeness | >95% | 80-95% | <80% |
| Link Health | 100% | >95% | <95% |
| Content Freshness | <6mo old | 6-12mo old | >12mo old |
| Test Coverage | >90% | 75-90% | <75% |

---

## 4. Review Process

### 4.1 Pre-Commit Review

Before committing documentation changes:

```bash
# 1. Validate locally
python validation/run_validation.py --check all

# 2. Review your changes
git diff docs/

# 3. Check for common issues:
# - Broken links?
# - Consistent formatting?
# - Spell check passed?
# - Examples work?

# 4. Test if docs reference code
# - Code still exists?
# - APIs haven't changed?
# - Examples still accurate?

# 5. Commit with message
git commit -m "docs: [component] [change description]"
```

### 4.2 PR Review Guidelines

When reviewing a PR that touches docs:

**Checklist:**
- [ ] Links are valid (no broken references)
- [ ] Formatting is consistent with existing docs
- [ ] Grammar and spelling correct
- [ ] Technical accuracy verified
- [ ] Examples tested and working
- [ ] Related docs updated
- [ ] LIBRARY_INDEX.md updated if new content
- [ ] No personally identifiable information

**Comment Template:**
```markdown
Documentation Review:
- [x] Links valid
- [x] Formatting consistent
- [x] Technical accuracy verified
- [x] Examples tested

Approved for merge ✅
```

---

## 5. Tool Support & Scripts

### 5.1 Validation Scripts

Location: `validation/`

**Script: `run_validation.py`**
```python
#!/usr/bin/env python3
"""Run all documentation validation checks."""

def main():
    checks = {
        'links': check_links,
        'content': check_content_structure,
        'schema': check_schema,
        'coverage': check_coverage,
        'spelling': check_spelling,
    }
    
    results = {}
    for name, check_fn in checks.items():
        print(f"Running {name} check...")
        results[name] = check_fn()
    
    # Print report
    print_report(results)
    
    # Update metrics
    if all(results.values()):
        update_metrics_dashboard()
```

**Script: `check_links.py`**
```python
def check_links() -> bool:
    """Validate all internal and external links."""
    broken = []
    for md_file in Path('docs').rglob('*.md'):
        for link in extract_links(md_file):
            if not validate_link(link):
                broken.append((md_file, link))
    
    if broken:
        print(f"❌ {len(broken)} broken links found")
        return False
    print("✅ All links valid")
    return True
```

### 5.2 Maintenance Scripts

**Script: `update_library_index.py`**

Auto-generates LIBRARY_INDEX.md when new content added:

```bash
# Run after adding agents/workflows/skills
python scripts/update_library_index.py

# Scans all agents/, workflows/, skills/
# Updates LIBRARY_INDEX.md with new entries
# Maintains alphabetical order
# Updates link references
```

**Script: `sync_tests_to_docs.py`**

Keep test documentation in sync with test code:

```bash
# Run after major test changes
python scripts/sync_tests_to_docs.py

# Extracts docstrings from test files
# Updates COVERAGE_REPORT.validation.md
# Ensures test docs match actual tests
```

---

## 6. Maintenance Schedule

### Daily
- Monitor error logs for documentation issues
- Address broken links if reported

### Weekly (Monday)
```bash
python validation/run_validation.py --check all
# Review report
# File issues for any problems
```

### Bi-weekly (Wednesday)
- Manual documentation review (see 1.2)
- Spot-check 5-10 docs for clarity/accuracy
- Update any outdated content

### Monthly (1st of month)
```bash
python validation/run_validation.py --metrics
# Updates QUALITY_METRICS.md
# Tracks trends
# Identifies patterns
```

### Quarterly (Jan/Apr/Jul/Oct)
- Comprehensive documentation audit
- Update outdated content
- Plan improvements
- Review feedback

### Annually
- Major documentation review
- Plan next year improvements
- Refactor if needed
- Archive old versions

---

## 7. Issue Tracking

### 7.1 Documentation Issues

When you find a documentation problem:

**File an issue with:**
- [ ] File/section affected
- [ ] Problem description (what's wrong)
- [ ] Impact (how it affects users)
- [ ] Suggested fix (if you know it)
- [ ] Priority (critical/high/medium/low)

**Example:**
```
Title: [Docs] Broken link in PERSONA_GUIDES.md

File: docs/PERSONA_GUIDES.md (Backend Developer section)
Problem: Link to "API_REFERENCE.reference.md" returns 404
Impact: Users can't find API documentation
Fix: Update link path to correct location
Priority: High
```

### 7.2 Issue Resolution SLA

| Priority | Response Time | Fix Time |
|----------|---------------|----------|
| Critical | 24 hours | 2 days |
| High | 2 days | 1 week |
| Medium | 1 week | 2 weeks |
| Low | 2 weeks | 1 month |

---

## 8. Continuous Improvement

### 8.1 Feedback Loop

**Collect feedback from:**
- GitHub issues mentioning docs
- User questions in discussions
- Support requests
- Code review comments

**Weekly review of feedback:**
```bash
# Check for issues tagged "documentation"
github cli api repos/[owner]/[repo]/issues --label documentation

# Prioritize based on frequency
# Address top complaints first
```

### 8.2 Documentation Debt

Track documentation that needs work:

**In TECHNICAL_DEBT.md, maintain section:**
```markdown
## Documentation Debt

### High Priority
- [ ] Update builder guides for new features
- [ ] Add examples for complex workflows
- [ ] Clarify error handling in API docs

### Medium Priority
- [ ] Expand PERSONA_GUIDES.md with more personas
- [ ] Add video walkthroughs (nice to have)
- [ ] Create troubleshooting FAQ

### Low Priority
- [ ] Refactor old documentation
- [ ] Improve formatting
- [ ] Add more examples
```

---

## 9. Documentation Standards

### 9.1 Writing Style

**Tone:** Professional, clear, helpful

**Guidelines:**
- Use active voice (avoid "is done" → "do")
- Be concise but complete
- Use examples liberally
- Link related content
- Define jargon on first use

**Example - BAD:**
```
The agent is used for debugging issues. Workflows can be created.
```

**Example - GOOD:**
```
Use the Debug Agent to diagnose production issues systematically.
Create workflows to document repeating debugging patterns.
See [QUICKSTART.md](QUICKSTART.md) for common workflows.
```

### 9.2 Formatting Standards

**Markdown:**
```markdown
# Main Title (h1)
## Section (h2)
### Subsection (h3)

**Bold** for emphasis
`code` for inline code
[Links](to-relevant-docs) for references

- Bullet lists for items
1. Numbered lists for steps

> Blockquotes for important notes

| Table | Format |
|-------|--------|
| For | Data |
```

**Code Examples:**
```markdown
\`\`\`python
# Always specify language
def example():
    pass
\`\`\`

Output should be in a note:
> Output: 
> ```
> result here
> ```
```

---

## 10. Getting Help

### For Documentation Questions:
- Check [QUICKSTART.md](../QUICKSTART.md)
- Check [PERSONA_GUIDES.md](../PERSONA_GUIDES.md)
- Search [LIBRARY_INDEX.md](../LIBRARY_INDEX.md)

### For Documentation Issues:
- File issue with "documentation" label
- Include: file, problem, impact, suggested fix

### For Documentation Contributions:
- Follow standards in section 9
- Follow review process in section 4
- Run validation before submitting PR

---

## Appendix A: Validation Commands

```bash
# Check all docs
python validation/run_validation.py --check all

# Check specific category
python validation/run_validation.py --check links
python validation/run_validation.py --check content
python validation/run_validation.py --check schema

# Update metrics
python validation/run_validation.py --metrics

# Spell check
python validation/run_validation.py --spellcheck

# Generate report
python validation/run_validation.py --report html
```

---

## Appendix B: CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/docs-validate.yml
name: Documentation Validation

on:
  push:
    paths:
      - 'docs/**'
      - '**.md'
  pull_request:
    paths:
      - 'docs/**'
      - '**.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Validate documentation
        run: python validation/run_validation.py --check all
      - name: Check for broken links
        run: python validation/run_validation.py --check links
      - name: Validate content structure
        run: python validation/run_validation.py --check content
      - name: Update metrics
        run: python validation/run_validation.py --metrics
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Apr 11, 2026 | Initial version - created for v2.1.0 release |

---

**Next Review Date:** May 11, 2026  
**Last Updated:** April 11, 2026  
**Owner:** Engineering Team
