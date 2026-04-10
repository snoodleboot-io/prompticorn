# Language-Based Skill/Workflow Filtering - Implementation Guide

## Quick Start

### Step 1: Update Your Config

To enable language-based filtering, add the language to your project config:

```python
config = {
    "variant": "minimal",  # or "verbose"
    "spec": {
        "language": "python",  # Add this line
        # ... other spec fields
    }
}
```

### Step 2: Use PromptBuilder

```python
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder

# Create builder
builder = PromptBuilder("kilo")

# Build with language filtering
output_dir = Path("./output")
actions = builder.build(output_dir, config)

# Display results
for action in actions:
    print(action)
```

### Step 3: Verify Filtering

Check that only relevant skills are included:

```python
output_dir = Path("./output")

# List skill files
skills_dir = output_dir / ".kilo" / "skills"
for skill_dir in skills_dir.iterdir():
    print(f"Skill: {skill_dir.name}")
```

---

## Supported Languages

Add one of these language codes to your config:

| Language | Code | Use Case |
|----------|------|----------|
| Python | `python` | Data science, APIs, CLI tools |
| TypeScript | `typescript` | Web apps, Node.js backends |
| JavaScript | `javascript` | Frontend, Node.js |
| Go | `go` | Microservices, DevOps |
| Rust | `rust` | Systems programming, performance |
| Java | `java` | Enterprise applications |
| C# | `csharp` | .NET applications |
| C++ | `cpp` | Performance-critical systems |
| PHP | `php` | Web servers, CMS |
| Ruby | `ruby` | Rails applications, scripting |
| Swift | `swift` | iOS/macOS development |
| Kotlin | `kotlin` | Android development |
| SQL | `sql` | Database work |
| Bash | `bash` | Shell scripts, DevOps |

---

## Complete Working Example: Python Project

### Scenario: Building instructions for a Python FastAPI backend

**Step 1: Create config**

```python
config = {
    "variant": "minimal",
    "spec": {
        "language": "python",
        "framework": "fastapi",
        "orm": "sqlalchemy",
        "testing_framework": "pytest",
    }
}
```

**Step 2: Build instructions**

```python
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder

# Create builder for Kilo IDE
builder = PromptBuilder("kilo")

# Build in project directory
project_root = Path("/path/to/my-fastapi-project")
actions = builder.build(project_root, config)

# Display what was created
print("Generated Instructions:")
for action in actions:
    if action.startswith("✓"):
        print(f"  {action}")
    else:
        print(f"  {action}")
```

**Step 3: Verify output**

```bash
# Check generated files
ls -la my-fastapi-project/.kilo/
ls -la my-fastapi-project/.kilo/agents/
ls -la my-fastapi-project/.kilo/skills/

# Files should include Python-specific skills:
# - python-type-hints-enforcement
# - python-async-patterns
# - python-property-usage
# - test-aaa-structure
# - pytest-fixtures
```

**Step 4: Use in Kilo**

```bash
# In Kilo IDE, the code agent will now use Python-specific guidance:
# - Type hints enforcement
# - Async/await patterns
# - Property usage guidelines
# - Pytest testing patterns
# - Pydantic validation

# Non-Python skills are excluded:
# - typescript-strict-mode-enforcement
# - go-interface-design
# - rust-ownership-patterns
```

---

## Complete Working Example: TypeScript Project

### Scenario: Building instructions for a Next.js frontend

**Step 1: Create config**

```python
config = {
    "variant": "verbose",
    "spec": {
        "language": "typescript",
        "framework": "nextjs",
        "testing_framework": "vitest",
        "package_manager": "pnpm",
    }
}
```

**Step 2: Build instructions**

```python
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder

# Create builder for Cursor
builder = PromptBuilder("cursor")

# Build in project directory
project_root = Path("/path/to/my-nextjs-app")
actions = builder.build(project_root, config)

for action in actions:
    print(action)
```

**Step 3: Verify output**

```bash
# Check generated files
cat my-nextjs-app/.cursorrules

# Content should include TypeScript-specific guidance:
# - Strict mode enforcement
# - Union type patterns
# - Never type usage
# - Vitest best practices
# - Component testing patterns
```

---

## Configuration by Tool

### Kilo CLI

```python
builder = PromptBuilder("kilo")

config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}

actions = builder.build(Path("."), config)
```

**Output Structure:**
```
.kilo/
  agents/
    code.md
    architect.md
    test.md
    review.md
  skills/
    python-type-hints-enforcement/
      SKILL.md
    python-async-patterns/
      SKILL.md
    ...
  commands/
    feature-workflow.md
    python-testing-workflow.md
    ...
```

### Cline (VS Code)

```python
builder = PromptBuilder("cline")

config = {
    "variant": "minimal",
    "spec": {"language": "typescript"}
}

actions = builder.build(Path("."), config)
```

**Output Structure:**
```
.clinerules          # Combined agent instructions
.cline/
  skills/
    typescript-strict-mode-enforcement/
      SKILL.md
    ...
```

### Claude (Claude.ai)

```python
builder = PromptBuilder("claude")

config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}

actions = builder.build(Path("."), config)
```

**Output Structure:**
```
custom_instructions/
  code.json          # JSON format for Claude
  architect.json
  test.json
```

### Copilot (GitHub)

```python
builder = PromptBuilder("copilot")

config = {
    "variant": "minimal",
    "spec": {"language": "go"}
}

actions = builder.build(Path("."), config)
```

**Output Structure:**
```
.github/
  copilot-instructions.md
  skills/
    go-interface-design.md
    go-concurrency-patterns.md
```

### Cursor

```python
builder = PromptBuilder("cursor")

config = {
    "variant": "minimal",
    "spec": {"language": "rust"}
}

actions = builder.build(Path("."), config)
```

**Output Structure:**
```
.cursorrules                    # Main rules file
.cursor/
  skills/
    rust-ownership-patterns/
      SKILL.md
    rust-trait-design/
      SKILL.md
```

---

## Advanced Usage

### Filtering with Custom Agent

```python
from promptosaurus.prompt_builder import PromptBuilder
from promptosaurus.ir.models.agent import Agent

builder = PromptBuilder("kilo")

# Create custom agent
custom_agent = Agent(
    name="my-agent",
    description="My custom agent",
    system_prompt="Custom system prompt",
    tools=["editor"],
    skills=[
        "python-type-hints-enforcement",
        "typescript-strict-mode-enforcement",
        "feature-planning",
    ],
    workflows=["feature-workflow"],
)

# Filter for Python
filtered = builder._filter_agent_for_language(custom_agent, "python")

# Result: only Python skills included
assert "python-type-hints-enforcement" in filtered.skills
assert "typescript-strict-mode-enforcement" not in filtered.skills
```

### Filtering Subagents

```python
# For more specific subagent filtering:
filtered_subagent = builder._filter_subagent_for_language(
    agent_name="code",
    subagent_name="feature",
    language="python"
)

# Uses python/code/feature mapping if available
```

### Checking Mapping Registry

```python
from promptosaurus.ir.loaders.language_skill_mapping_loader import LanguageSkillMappingLoader

loader = LanguageSkillMappingLoader("language_skill_mapping.yaml")

# Get all skills for Python
python_skills = loader.get_skills_for_language("python")
print(f"Python has {len(python_skills)} skills")

# Get Python + Code + Feature specific skills
python_code_feature = loader.get_skills_for_language("python", "code/feature")
print(f"Python/Code/Feature has {len(python_code_feature)} skills")

# Check if language is supported
if loader.has_language("python"):
    print("Python is supported")

# Check if language/subagent combination exists
if loader.has_subagent("python", "code/feature"):
    print("python/code/feature mapping exists")
```

---

## Troubleshooting

### Issue: Mapping file not found

**Error:**
```
FileNotFoundError: Mapping file not found: .../language_skill_mapping.yaml
```

**Solution:**
- Verify `language_skill_mapping.yaml` exists in project root
- Check file path: should be at `{project_root}/language_skill_mapping.yaml`
- Ensure file is readable

**Workaround:**
If file is missing, filtering is disabled (graceful degradation) - all skills included.

### Issue: Language not found in mapping

**Error:**
```
# No error, but too few skills returned
```

**Solution:**
1. Check language code is correct (case-sensitive)
2. Verify language exists in `language_skill_mapping.yaml`
3. Check priority resolution:
   ```python
   loader = LanguageSkillMappingLoader("language_skill_mapping.yaml")
   
   # Debug: get skills at each level
   all_skills = loader.get_skills_for_language("unknown")
   # Will return global "all" skills only
   ```

### Issue: Skills not being filtered

**Likely Causes:**
1. Language not specified in config
2. Skills don't exist in mapping for that language
3. Mapping loader not initialized

**Debug:**
```python
from promptosaurus.prompt_builder import PromptBuilder

builder = PromptBuilder("kilo")

# Check loader exists
if builder.language_skill_loader:
    print("Loader initialized")
else:
    print("No loader - check if mapping file exists")

# Check language in mapping
if builder.language_skill_loader.has_language("python"):
    print("Python language supported")
else:
    print("Python not in mapping")

# Get skills for language
skills = builder.language_skill_loader.get_skills_for_language("python")
print(f"Python skills: {skills}")
```

### Issue: Performance slow with large projects

**Solution:**
1. Use minimal variant instead of verbose
2. Filter at config level before calling build
3. Consider caching filtered agents if building multiple times

```python
# Use minimal variant (faster)
config = {
    "variant": "minimal",  # Not "verbose"
    "spec": {"language": "python"}
}

# Or filter once, reuse result
filtered_agent = builder._filter_agent_for_language(agent, "python")
# Use filtered_agent multiple times
```

---

## Best Practices

### 1. Always Specify Language in Config

Good:
```python
config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}
```

Less Good (no filtering):
```python
config = {"variant": "minimal"}
```

### 2. Use Correct Language Code

Good:
```python
"language": "python"      # matches mapping key
"language": "typescript"  # matches mapping key
```

Bad:
```python
"language": "Python"      # wrong case
"language": "py"          # not in mapping
"language": "node.js"     # use "javascript" instead
```

### 3. Match Agent Names to Mapping

The mapping uses lowercase agent names:
- `code`
- `architect`
- `test`
- `review`
- `debug`
- `refactor`

When using subagents, use the same naming:
- `code/feature` (not `code/Feature`)
- `architect/data-model` (not `architect/DataModel`)

### 4. Check Mapping Before Customizing

Before adding custom skills, check the mapping:

```python
loader = LanguageSkillMappingLoader("language_skill_mapping.yaml")
python_skills = loader.get_skills_for_language("python")

# Is your skill already there?
if "my-custom-skill" in python_skills:
    print("Already in mapping")
else:
    print("Add to language_skill_mapping.yaml")
```

### 5. Test Filtering Before Deploy

```python
# Test with dummy config
test_config = {
    "variant": "minimal",
    "spec": {"language": "python"}
}

# Do dry run first
actions = builder.build(test_dir, test_config, dry_run=True)

# Then actual build
actions = builder.build(output_dir, test_config, dry_run=False)
```

---

## Migration from Unfiltered to Filtered

If you have existing projects without filtering:

### Step 1: Add language to config

```diff
  config = {
      "variant": "minimal",
+     "spec": {"language": "python"}
  }
```

### Step 2: Rebuild

```bash
python3 -c "
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder

builder = PromptBuilder('kilo')
config = {
    'variant': 'minimal',
    'spec': {'language': 'python'}
}
actions = builder.build(Path('.'), config)
for action in actions:
    print(action)
"
```

### Step 3: Review changes

```bash
# Compare old vs new
git diff .kilo/agents/
git diff .kilo/skills/

# Should see:
# - Language-specific skills added
# - Language-incompatible skills removed
# - Workflows filtered by language
```

### Step 4: Commit changes

```bash
git add .kilo/
git commit -m "feat: add language-based skill filtering for Python"
```

---

## FAQ

**Q: Do I have to specify a language?**
A: No. If not specified, all skills/workflows included (backward compatible).

**Q: Can I use multiple languages?**
A: Build once per language with different configs.

**Q: What if my project uses multiple languages?**
A: Either:
1. Build without language (get all skills)
2. Build multiple times, one per language

**Q: Is filtering applied to tools?**
A: No. Tools are language-agnostic and always included.

**Q: Can I add custom skills to the mapping?**
A: Yes, edit `language_skill_mapping.yaml`. See comments in file.

**Q: What happens if mapping file is missing?**
A: Graceful degradation - filtering disabled, all skills included.

**Q: Can I filter subagents?**
A: Yes, use `_filter_subagent_for_language()` method.

**Q: Is filtering slow?**
A: No. Filtering completes in < 1ms for typical agents.

**Q: Does this break existing projects?**
A: No. Fully backward compatible. Don't specify language to get old behavior.

---

## See Also

- `LANGUAGE_SKILL_FILTERING.md` - Detailed architecture documentation
- `TEST_SCENARIOS_LANGUAGE_FILTERING.md` - Comprehensive test scenarios
- `language_skill_mapping.yaml` - Complete skill/workflow mappings
- `promptosaurus/prompt_builder.py` - Implementation code
