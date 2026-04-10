# Test Scenarios for Language-Based Skill/Workflow Filtering

## Overview

This document outlines comprehensive test scenarios for verifying that language-based skill/workflow filtering in PromptBuilder works correctly across different language and agent combinations.

## Unit Test Scenarios

### Scenario 1: Filter Agent with Python Language Specified

**Setup:**
```python
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder
from promptosaurus.ir.models.agent import Agent

builder = PromptBuilder("kilo")

# Create a test agent with mixed skills
agent = Agent(
    name="code",
    description="Code writing agent",
    system_prompt="You are a code agent",
    tools=["editor", "terminal"],
    skills=[
        "feature-planning",
        "incremental-implementation",
        "python-type-hints-enforcement",
        "typescript-strict-mode-enforcement",
        "go-interface-design",
    ],
    workflows=[
        "feature-workflow",
        "python-testing-workflow",
        "typescript-testing-workflow",
    ],
    subagents=["feature", "boilerplate"],
    permissions={"max_tokens": 4000}
)
```

**Action:**
```python
filtered = builder._filter_agent_for_language(agent, "python")
```

**Expected Results:**
```python
# Should have Python-specific skills
assert "python-type-hints-enforcement" in filtered.skills
assert "incremental-implementation" in filtered.skills
assert "feature-planning" in filtered.skills

# Should NOT have non-Python skills
assert "typescript-strict-mode-enforcement" not in filtered.skills
assert "go-interface-design" not in filtered.skills

# Should have Python-compatible workflows
assert "feature-workflow" in filtered.workflows
assert "python-testing-workflow" in filtered.workflows

# Should NOT have TypeScript-specific workflows
assert "typescript-testing-workflow" not in filtered.workflows

# Tools should never be filtered
assert filtered.tools == ["editor", "terminal"]

# Subagents should be preserved
assert filtered.subagents == ["feature", "boilerplate"]

# Permissions should be preserved
assert filtered.permissions == {"max_tokens": 4000}

# Name and description unchanged
assert filtered.name == "code"
assert filtered.description == "Code writing agent"
```

---

### Scenario 2: Filter Agent with No Language Specified

**Setup:**
```python
agent = Agent(
    name="review",
    description="Code review agent",
    system_prompt="You are a review agent",
    tools=["diff", "lint"],
    skills=["code-quality-checklist", "performance-analysis"],
    workflows=["review-workflow"],
    subagents=["code"],
)
```

**Action:**
```python
filtered = builder._filter_agent_for_language(agent, None)
```

**Expected Results:**
```python
# Should return same agent (no filtering)
assert filtered is agent

# All properties unchanged
assert filtered.skills == agent.skills
assert filtered.workflows == agent.workflows
assert filtered.tools == agent.tools
```

---

### Scenario 3: Filter Agent with TypeScript Language

**Setup:**
```python
agent = Agent(
    name="test",
    description="Test writing agent",
    system_prompt="You are a test agent",
    tools=["terminal"],
    skills=[
        "test-aaa-structure",
        "typescript-strict-mode-enforcement",
        "python-type-hints-enforcement",
        "vitest-best-practices",
        "pytest-fixtures",
    ],
    workflows=[
        "unit-testing-workflow",
        "typescript-testing-workflow",
        "python-testing-workflow",
    ],
)
```

**Action:**
```python
filtered = builder._filter_agent_for_language(agent, "typescript")
```

**Expected Results:**
```python
# Should include TypeScript testing skills
assert "typescript-strict-mode-enforcement" in filtered.skills
assert "vitest-best-practices" in filtered.skills
assert "test-aaa-structure" in filtered.skills

# Should NOT include Python testing skills
assert "python-type-hints-enforcement" not in filtered.skills
assert "pytest-fixtures" not in filtered.skills

# Should include universal testing workflow
assert "unit-testing-workflow" in filtered.workflows

# Should include TypeScript workflow
assert "typescript-testing-workflow" in filtered.workflows

# Should NOT include Python workflow
assert "python-testing-workflow" not in filtered.workflows
```

---

### Scenario 4: Filter with Mapping Loader Unavailable

**Setup:**
```python
builder = PromptBuilder("kilo")
builder.language_skill_loader = None  # Simulate missing loader

agent = Agent(
    name="code",
    description="Code agent",
    system_prompt="You are code",
    tools=["editor"],
    skills=["python-async-patterns", "typescript-strict-mode"],
    workflows=["feature-workflow"],
)
```

**Action:**
```python
filtered = builder._filter_agent_for_language(agent, "python")
```

**Expected Results:**
```python
# Should return unchanged agent (graceful degradation)
assert filtered is agent
assert filtered.skills == agent.skills
assert filtered.workflows == agent.workflows
```

---

### Scenario 5: Subagent Filtering with Language+Subagent Combination

**Setup:**
```python
# Test agent in registry: code/feature
subagent = Agent(
    name="code/feature",
    description="Feature implementation subagent",
    system_prompt="You implement features",
    tools=["editor"],
    skills=[
        "feature-planning",
        "incremental-implementation",
        "python-type-hints-enforcement",
        "python-async-patterns",
        "typescript-union-type-patterns",
    ],
    workflows=[
        "feature-workflow",
        "python-testing-workflow",
    ],
)

# Mock registry to return this subagent
builder.registry.add_agent("code/feature", subagent)
```

**Action:**
```python
filtered = builder._filter_subagent_for_language("code", "feature", "python")
```

**Expected Results:**
```python
# Should get Python-specific skills for code/feature combination
assert "python-type-hints-enforcement" in filtered.skills
assert "python-async-patterns" in filtered.skills
assert "feature-planning" in filtered.skills

# Should NOT get TypeScript-specific skills
assert "typescript-union-type-patterns" not in filtered.skills

# Should include workflows for this combination
assert "python-testing-workflow" in filtered.workflows
```

---

### Scenario 6: Priority Resolution - Language/Agent/Subagent

**Objective:** Verify the priority resolution order works correctly

**Setup:**
```python
# Assuming mapping has:
# all: global skills
# python: python-specific skills
# python/code: python+code skills
# python/code/feature: python+code+feature skills

loader = builder.language_skill_loader
```

**Test Cases:**

#### 6a: Language-level resolution (no subagent)
```python
skills = loader.get_skills_for_language("python")
# Should include:
# - all: feature-planning, post-implementation-checklist
# - python: python-type-hints-enforcement, python-async-patterns
# Should NOT include:
# - typescript-specific skills
# - go-specific skills
```

#### 6b: Language + Subagent resolution (more specific)
```python
skills = loader.get_skills_for_language("python", subagent="code/feature")
# Should prefer python/code/feature mapping if it exists
# Falls back to python/code, then python, then all
```

---

## Integration Test Scenarios

### Integration Test 1: Full Build with Python Language Filtering

**Setup:**
```python
import tempfile
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder

builder = PromptBuilder("kilo")

config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}

with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir)
```

**Action:**
```python
    actions = builder.build(output_dir, config)
```

**Verification Steps:**
1. Check that build completed without errors
   ```python
   assert all(a.startswith("✓") for a in actions)
   ```

2. Verify agent files written
   ```python
   agents_dir = output_dir / ".kilo" / "agents"
   assert (agents_dir / "code.md").exists()
   assert (agents_dir / "architect.md").exists()
   ```

3. Verify skill files are Python-only
   ```python
   skills_dir = output_dir / ".kilo" / "skills"
   python_skill_files = list(skills_dir.glob("**/SKILL.md"))
   
   for skill_file in python_skill_files:
       content = skill_file.read_text()
       # Should not contain TypeScript-specific guidance
       assert "TypeScript strict mode" not in content
   ```

4. Verify workflow files are Python-compatible
   ```python
   commands_dir = output_dir / ".kilo" / "commands"
   if commands_dir.exists():
       workflow_files = list(commands_dir.glob("*.md"))
       assert len(workflow_files) > 0
   ```

---

### Integration Test 2: Full Build with TypeScript Language Filtering

**Setup:**
```python
builder = PromptBuilder("kilo")

config = {
    "variant": "verbose",
    "spec": {"language": "typescript"}
}

with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir)
```

**Action:**
```python
    actions = builder.build(output_dir, config)
```

**Verification Steps:**
1. Verify TypeScript-specific skills are included
   ```python
   agent_file = output_dir / ".kilo" / "agents" / "code.md"
   content = agent_file.read_text()
   assert "typescript-strict-mode-enforcement" in content or \
          "TypeScript" in content
   ```

2. Verify Python-specific skills are NOT included
   ```python
   # Skills directory or agent content should not contain
   # Python-only guidance
   for skill_file in skills_dir.glob("**/SKILL.md"):
       content = skill_file.read_text()
       # May not be perfect, but should lean TypeScript
   ```

---

### Integration Test 3: Build with No Language (Backward Compatibility)

**Setup:**
```python
builder = PromptBuilder("kilo")

# No language specified in config
config = {"variant": "minimal"}

with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir)
```

**Action:**
```python
    actions = builder.build(output_dir, config)
```

**Verification Steps:**
1. Build completes successfully
   ```python
   assert all(a.startswith("✓") or a.startswith("✗") for a in actions)
   ```

2. All skills are included (no filtering)
   ```python
   skills_dir = output_dir / ".kilo" / "skills"
   skill_files = list(skills_dir.glob("**/SKILL.md"))
   
   # Should include skills from multiple languages
   has_python = any("python" in str(f).lower() for f in skill_files)
   has_typescript = any("typescript" in str(f).lower() for f in skill_files)
   # (Verify based on actual skill directory structure)
   ```

---

### Integration Test 4: Multiple Language Builds (Verify Isolation)

**Objective:** Ensure filtering for one language doesn't affect another

**Setup:**
```python
builder = PromptBuilder("kilo")

languages = ["python", "typescript", "go"]
outputs = {}
```

**Action:**
```python
for lang in languages:
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        config = {
            "variant": "minimal",
            "spec": {"language": lang}
        }
        actions = builder.build(output_dir, config)
        outputs[lang] = output_dir
```

**Verification Steps:**
1. Each language built successfully
   ```python
   for lang in languages:
       assert outputs[lang].exists()
   ```

2. Python build only has Python skills
   ```python
   python_skills = [f.name for f in (outputs["python"] / ".kilo" / "skills").glob("*")]
   # Should not include TypeScript-specific skills
   ```

3. TypeScript build only has TypeScript skills
   ```python
   ts_skills = [f.name for f in (outputs["typescript"] / ".kilo" / "skills").glob("*")]
   # Should not include Python-specific skills
   ```

---

### Integration Test 5: Dry Run Mode (No Files Written, But Filtering Still Applied)

**Setup:**
```python
builder = PromptBuilder("kilo")

config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}

with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir)
```

**Action:**
```python
    # Dry run (dry_run=True)
    actions = builder.build(output_dir, config, dry_run=True)
```

**Verification Steps:**
1. Actions returned (planning phase only)
   ```python
   assert len(actions) == 0  # Dry run returns no write actions
   ```

2. No files actually written
   ```python
   assert not (output_dir / ".kilo").exists()
   ```

3. Filtering logic still executed (verify with spy/mock if needed)

---

## Edge Case Test Scenarios

### Edge Case 1: Agent with Empty Skills

**Setup:**
```python
agent = Agent(
    name="empty",
    description="Agent with no skills",
    system_prompt="Empty",
    tools=["tool"],
    skills=[],  # Empty!
    workflows=["workflow"],
)
```

**Action:**
```python
filtered = builder._filter_agent_for_language(agent, "python")
```

**Expected Results:**
```python
assert filtered.skills == []
assert filtered.workflows == ["workflow"]  # Workflows still processed
```

---

### Edge Case 2: Invalid Language Code

**Setup:**
```python
agent = Agent(
    name="test",
    description="Test",
    system_prompt="Test",
    tools=[],
    skills=["python-async-patterns"],
    workflows=["feature-workflow"],
)
```

**Action:**
```python
# Language code doesn't exist in mapping
filtered = builder._filter_agent_for_language(agent, "unknown-lang")
```

**Expected Results:**
```python
# Should gracefully fall back to global defaults
# Actual behavior depends on LanguageSkillMappingLoader implementation
# Either: returns agent unchanged or filters using only "all" defaults
```

---

### Edge Case 3: Very Large Agent with Many Skills

**Setup:**
```python
# Create agent with 100+ skills
large_agent = Agent(
    name="large",
    description="Large agent",
    system_prompt="Large",
    tools=["editor"],
    skills=[f"skill-{i}" for i in range(100)],
    workflows=[f"workflow-{i}" for i in range(50)],
)
```

**Action:**
```python
import time
start = time.time()
filtered = builder._filter_agent_for_language(large_agent, "python")
elapsed = time.time() - start
```

**Expected Results:**
```python
# Should complete in reasonable time (< 10ms)
assert elapsed < 0.01

# Skills should be properly filtered
assert len(filtered.skills) < len(large_agent.skills)
```

---

## Performance Test Scenarios

### Performance Test 1: Filtering Overhead

**Objective:** Measure filtering performance

```python
import time
from promptosaurus.prompt_builder import PromptBuilder
from promptosaurus.ir.models.agent import Agent

builder = PromptBuilder("kilo")

agent = Agent(
    name="perf-test",
    description="Performance test",
    system_prompt="Perf",
    tools=["editor"],
    skills=[f"skill-{i}" for i in range(50)],
    workflows=[f"workflow-{i}" for i in range(20)],
)

# Measure with filtering
start = time.time()
for _ in range(100):
    builder._filter_agent_for_language(agent, "python")
with_filter = time.time() - start

# Measure without filtering (language=None)
start = time.time()
for _ in range(100):
    builder._filter_agent_for_language(agent, None)
without_filter = time.time() - start

print(f"With filter: {with_filter:.4f}s")
print(f"Without filter: {without_filter:.4f}s")
print(f"Overhead: {(with_filter - without_filter) / 100 * 1000:.2f}ms per call")
```

**Expected Results:**
```python
# Filtering overhead should be minimal
assert (with_filter - without_filter) < 0.1  # < 100ms total for 100 calls
assert (with_filter - without_filter) / 100 < 0.001  # < 1ms per call
```

---

### Performance Test 2: Loader Initialization

**Objective:** Measure YAML parsing performance

```python
import time
from promptosaurus.ir.loaders.language_skill_mapping_loader import LanguageSkillMappingLoader

# First load (parses YAML)
start = time.time()
loader1 = LanguageSkillMappingLoader("language_skill_mapping.yaml")
first_load = time.time() - start

# Repeated loads (might be cached)
loads = []
for _ in range(10):
    start = time.time()
    loader = LanguageSkillMappingLoader("language_skill_mapping.yaml")
    skills = loader.get_skills_for_language("python")
    loads.append(time.time() - start)

print(f"First load: {first_load:.4f}s")
print(f"Avg subsequent loads: {sum(loads) / len(loads):.4f}s")
```

**Expected Results:**
```python
# Should be fast enough for CLI tool
assert first_load < 1.0  # First parse < 1 second
assert sum(loads) / len(loads) < 0.01  # Repeated loads < 10ms
```

---

## Regression Test Scenarios

### Regression Test 1: Verify Backward Compatibility

**Objective:** Ensure existing code still works without changes

```python
from promptosaurus.prompt_builder import PromptBuilder

# Old code (no language in config)
builder = PromptBuilder("kilo")
old_config = {"variant": "minimal"}  # No "spec"

# Should work exactly as before
actions = builder.build(output_dir, old_config)
assert len(actions) > 0
assert all(isinstance(a, str) for a in actions)
```

---

### Regression Test 2: Tool-Specific Output Unchanged

**Objective:** Verify filtering doesn't break tool-specific output formats

**For Each Tool:**
```python
for tool in ["kilo", "cline", "claude", "copilot", "cursor"]:
    builder = PromptBuilder(tool)
    
    config = {
        "variant": "minimal",
        "spec": {"language": "python"}
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        actions = builder.build(Path(tmpdir), config)
        
        # Verify expected files for this tool
        if tool == "kilo":
            assert (Path(tmpdir) / ".kilo" / "agents").exists()
        elif tool == "cline":
            assert (Path(tmpdir) / ".clinerules").exists()
        elif tool == "claude":
            assert (Path(tmpdir) / "custom_instructions").exists()
        elif tool == "copilot":
            assert (Path(tmpdir) / ".github" / "copilot-instructions.md").exists()
        elif tool == "cursor":
            assert (Path(tmpdir) / ".cursorrules").exists()
```

---

## Manual Testing Checklist

When deploying language filtering feature:

- [ ] Filter Python project and verify Python-specific skills included
- [ ] Filter TypeScript project and verify TypeScript-specific skills included
- [ ] Build without language and verify all skills included
- [ ] Check missing mapping file doesn't crash
- [ ] Verify file output structure unchanged
- [ ] Verify all tools (kilo, cline, claude, copilot, cursor) work
- [ ] Check performance with large projects (100+ agents)
- [ ] Verify dry-run mode works with filtering
- [ ] Test with real project configs
- [ ] Verify skill filenames match expectations
- [ ] Check workflow files written for Kilo only

---

## Test Execution

Run tests with:

```bash
# Unit tests
pytest tests/unit/builders/test_prompt_builder.py -v

# Integration tests
pytest tests/integration/test_prompt_build_cli.py -v

# All tests
pytest tests/ -v -k "language_filter or prompt_builder"

# With coverage
pytest tests/ --cov=promptosaurus.prompt_builder --cov-report=html
```

---

## Debugging Failed Tests

Common issues and solutions:

1. **Mapping file not found**
   - Verify `language_skill_mapping.yaml` exists at project root
   - Check file permissions (must be readable)

2. **Language not in mapping**
   - Verify language code matches mapping keys
   - Check YAML syntax in language_skill_mapping.yaml

3. **Skills filter incorrectly**
   - Verify skill names match exactly (case-sensitive)
   - Check priority resolution order

4. **Performance slower than expected**
   - Profile with `cProfile`
   - Check if YAML parsing is the bottleneck
   - Consider lazy loading or caching

5. **Subagent filtering not working**
   - Verify subagent exists in registry
   - Check `agent_name/subagent_name` format
   - Verify subagent has skills/workflows defined
