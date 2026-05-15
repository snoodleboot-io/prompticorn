# Language Integration Design

**Objective:** Enable dynamic skill/workflow inclusion and convention loading based on language selection, with configuration value templating.

## Problem Statement

Currently:
- ❌ Skills and workflows are not mapped to languages
- ❌ Core convention files are not auto-included based on language selection
- ❌ Configuration values (Python version, test framework) are not templated into output
- ❌ No way to have language-specific skills (e.g., pytest-fixtures for Python only)

## Proposed Solution - THREE PARTS

### Part 1: Language-Skills/Workflows Mapping

Add `languages: [...]` field to YAML frontmatter of all skills and workflows:

Example skill:
```markdown
---
name: incremental-implementation
description: Implement code incrementally
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
tools_needed: [edit, write, read]
---
```

Create `prompticorn/language_skill_mapping.yaml`:
```yaml
all:
  skills:
    - feature-planning
    - post-implementation-checklist
  workflows:
    - feature-workflow
    - review-workflow

python:
  skills:
    - incremental-implementation
    - test-aaa-structure
    - test-coverage-categories
  workflows:
    - testing-workflow
    - data-model-workflow

typescript:
   skills:
     - incremental-implementation
     - test-aaa-structure
   workflows:
     - testing-workflow
```

### Part 1.5: Subagent Compatibility Mapping

Skills and workflows need to declare which subagents they're compatible with.

#### Update Skill/Workflow Metadata

Add `subagents` field to YAML frontmatter:

```markdown
---
name: feature-planning
description: Plan feature implementation
languages: [python, typescript, javascript, ...]
subagents:
  - code/feature
  - code/bug-fix
  - architect/task-breakdown
tools_needed: [read]
---
```

Examples of subagent paths:
- `code/feature` - feature subagent under code agent
- `test/unit` - unit test subagent under test agent
- `architect/data-model` - data-model subagent under architect agent
- `all` - applicable to all subagents (if not restricted)

#### Update language_skill_mapping.yaml Structure

Change from:
```yaml
all:
  skills: [feature-planning, ...]
python:
  skills: [test-aaa-structure, ...]
```

To:
```yaml
all:  # Applied to all languages and subagents
  skills:
    - feature-planning
    - post-implementation-checklist

python:  # Python-specific, all subagents
  skills:
    - incremental-implementation
    - test-aaa-structure

python/code/feature:  # Python + code/feature subagent
  skills:
    - feature-planning
    - incremental-implementation
    - test-aaa-structure
  workflows:
    - feature-workflow
    - testing-workflow

python/test/unit:  # Python + test/unit subagent
  skills:
    - test-aaa-structure
    - test-coverage-categories
  workflows:
    - testing-workflow

typescript/code/feature:  # TypeScript + code/feature subagent
  skills:
    - feature-planning
    - incremental-implementation
  workflows:
    - feature-workflow
```

#### Subagent IR Should Have Languages Too

Update subagent frontmatter to declare language support:

```markdown
---
name: feature
description: Implement new features
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
tools: [read]
skills:
  - feature-planning
  - incremental-implementation
workflows:
  - feature-workflow
---
```

#### CoreFilesLoader Behavior

When loading core files for a subagent:
- Load based on parent agent's language (from config)
- Language determines which conventions to include
- All subagents of same agent share language conventions

#### Build Process Updated

During build for each subagent:

```python
language = config['spec']['language']
subagent_path = f"{agent_name}/{subagent_name}"

# Get skills/workflows for this combination
skills_workflows = language_skill_mapping.get(
    f"{language}/{subagent_path}",      # Specific combination
    language_skill_mapping.get(subagent_path, {})  # Fallback to subagent only
)

# Filter by language support (verify subagent supports language)
if language not in subagent['languages']:
    # Skip or warn - subagent doesn't support this language
    pass

# Use filtered skills/workflows
subagent['skills'] = skills_workflows.get('skills', [])
subagent['workflows'] = skills_workflows.get('workflows', [])
```

#### Registration Priority

When resolving skills/workflows for a subagent:

1. Check exact match: `{language}/{agent_name}/{subagent_name}`
2. Check language + subagent: `{language}/{subagent_name}` 
3. Check language only: `{language}`
4. Check subagent only: `{subagent_name}`
5. Check "all"

#### Examples

**Example 1: Python + code/feature subagent**

Mapping lookup: `python/code/feature`
Result:
```yaml
skills:
  - feature-planning
  - incremental-implementation
  - post-implementation-checklist
workflows:
  - feature-workflow
  - testing-workflow
```

Plus always included:
- Core language conventions (conventions-python.md)
- Core system files (system.md, conventions.md, session.md)

**Example 2: TypeScript + test/unit subagent**

Mapping lookup: `typescript/test/unit`
Result:
```yaml
skills:
  - test-aaa-structure
  - test-coverage-categories
workflows:
  - testing-workflow
```

Plus always included:
- Core language conventions (conventions-typescript.md)
- Core system files

**Example 3: Java + architect/data-model subagent**

Mapping lookup: `java/architect/data-model`
Result:
```yaml
skills:
  - data-model-discovery
  - mermaid-erd-creation
workflows:
  - data-model-workflow
```

Plus always included:
- Core language conventions (conventions-java.md)
- Core system files

#### Initial Revision

When adding language metadata to skills/workflows, ALSO add subagent compatibility:

```markdown
---
name: feature-planning
description: Plan implementation before coding
languages: [all]           # Works with all languages
subagents: [all]           # Works with all subagents
tools_needed: [read]
---
```

Or more restricted:

```markdown
---
name: test-aaa-structure
description: AAA test structure pattern
languages: [python, typescript, go, rust, java, csharp]
subagents: [test/unit, test/integration, code/feature]  # Only these subagents
tools_needed: [write]
---
```

### Part 2: Auto-Include Core Conventions by Language

Create `prompticorn/ir/loaders/core_files_loader.py`:

```python
class CoreFilesLoader:
    def get_core_files(self, language: str) -> dict[str, str]:
        """Get core files for a language.
        
        Always returns: system.md, conventions.md, session.md
        Plus language-specific: conventions-{language}.md if available
        """
```

Update builders to load core files based on language from config.

### Part 3: Template Configuration Values in Core Files

Convert core convention files to Jinja2 templates.

Current conventions-python.md has static values:
```
Language:             python
Runtime:              3.14
Package Manager:      uv
Test Framework:       pytest
```

Change to template syntax:
```
Language:             {{ language }}
Runtime:              {{ runtime }}
Package Manager:      {{ package_manager }}
Test Framework:       {{ test_framework }}
```

During build, render with actual config values from CLI questions.

## Implementation Plan

### Step 1: Add Language Metadata
- Add `languages: [...]` to all skills YAML frontmatter
- Add `languages: [...]` to all workflows YAML frontmatter
- Add `subagents: [...]` to all skills and workflows YAML frontmatter
- Create language_skill_mapping.yaml registry with language + subagent combinations

### Step 1.5: Add Subagent Language Support
- Add `languages: [...]` to all subagent frontmatter
- Update language_skill_mapping.yaml to include subagent-specific paths
- Create resolution priority rules for skill/workflow lookup

### Step 2: Create CoreFilesLoader
- Implement loader class
- Load core files by language
- Integrate with registry

### Step 3: Convert to Templates
- Update all conventions-{language}.md files to Jinja2
- Add template variables: language, runtime, package_manager, test_framework, linter, formatter, coverage_tool

### Step 4: Update Builders
- KiloBuilder includes core files + language-specific skills
- PromptBuilder filters skills by language
- Other builders follow same pattern

### Step 5: Update Prompt Build Logic
- Load language skill mapping
- Include "all" skills + language-specific skills
- Render core convention templates with config values

## Files to Create/Modify

Create:
- prompticorn/ir/loaders/core_files_loader.py
- prompticorn/ir/loaders/language_skill_mapping_loader.py
- prompticorn/ir/loaders/subagent_compatibility_resolver.py
- prompticorn/language_skill_mapping.yaml

Modify:
- All skills (add languages and subagents fields)
- All workflows (add languages and subagents fields)
- All subagents (add languages field)
- All conventions-{language}.md (convert to Jinja2)
- KiloBuilder, PromptBuilder, SubagentBuilder, other builders

## Result

When user runs CLI with Python config for code/feature subagent:
```
language: python
runtime: 3.12
test_framework: pytest
package_manager: uv
agent: code
subagent: feature
```

Output includes:
- Core system.md
- Core conventions.md  
- Python conventions (templated with actual values)
- Python + code/feature skills: feature-planning, incremental-implementation, test-aaa-structure
- Language-agnostic skills: post-implementation-checklist, feature-planning
- Python + code/feature workflows: feature-workflow, testing-workflow
- Language-agnostic workflows: review-workflow

Skills/workflows are filtered based on:
1. Exact match: `python/code/feature`
2. Language-only fallback: `python`
3. Subagent-only fallback: `code/feature` or `feature`
4. "all" category (always included)

All with dynamic values rendered into text.
Subagents must declare language support—if Python is not in subagent's `languages` field, it will be skipped with a warning.
