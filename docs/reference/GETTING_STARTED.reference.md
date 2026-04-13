# Getting Started with Phase 2A

**Version:** 2.0.0  
**Last Updated:** April 9, 2026

A quick guide to using Promptosaurus Phase 2A for unified AI agent prompt management across 5 coding assistants.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Building for All 5 Tools](#building-for-all-5-tools)
4. [Complete Examples](#complete-examples)
5. [CLI Command Reference](#cli-command-reference)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Using pip

```bash
pip install promptosaurus
```

### Using uv

```bash
uv add promptosaurus
```

### Using poetry

```bash
poetry add promptosaurus
```

### Verify Installation

```bash
promptosaurus --version
# Output: promptosaurus 2.0.0
```

---

## Quick Start (5 Minutes)

### 1. Create Project Structure

```bash
# Create agents directory
mkdir -p agents/architect/{minimal,verbose}

# Create first agent
touch agents/architect/{minimal,verbose}/prompt.md
```

### 2. Define Minimal Agent

**File: `agents/architect/minimal/prompt.md`**

```markdown
---
name: architect
description: Design system architecture
---

You are a software architect. Design:
- Data models and schemas
- Service boundaries
- API contracts
```

### 3. Define Verbose Agent

**File: `agents/architect/verbose/prompt.md`**

```markdown
---
name: architect
description: Design system architecture and data models
---

You are an expert software architect with deep knowledge of system design patterns.

Your responsibilities include:

**System Design:**
- Design scalable, maintainable systems
- Plan service boundaries and integration points
- Define deployment topologies

**Data Modeling:**
- Design normalized database schemas
- Plan for growth and scaling
- Implement proper indexing strategies

**API Design:**
- Define REST/GraphQL contracts
- Plan for versioning and backward compatibility
- Document endpoints and error handling

Focus on clarity, scalability, and maintainability.
```

### 4. Build for All Tools

```bash
promptosaurus build
```

**Output:**
```
✓ Built KiloBuilder (1.2ms)
✓ Built ClineBuilder (1.1ms)
✓ Built ClaudeBuilder (1.3ms)
✓ Built CursorBuilder (1.0ms)
✓ Built CopilotBuilder (0.9ms)
✓ Total: 5 tools in 5.5ms
```

### 5. Verify Files

```bash
# Check Kilo output
ls -la .kilo/agents/architect.md

# Check Cline output
grep -A5 "^# architect" .clinerules

# Check Claude output
jq '.[] | select(.name=="architect")' claude-agents.json | head -20
```

**Done!** 🎉 Your agent is now configured for all 5 tools.

---

## Building for All 5 Tools

### Understanding the 5 Builders

| Tool | Format | Use Case | Output |
|------|--------|----------|--------|
| **Kilo** | YAML + Markdown | Primary IDE agent framework | `.kilo/agents/*.md` |
| **Cline** | Markdown with `use_skill` | AI coding assistant with skills | `.clinerules` |
| **Claude** | JSON (Messages API) | Claude API integration | `claude-agents.json` |
| **Cursor** | Markdown rules | IDE rules file | `.cursorrules` |
| **Copilot** | YAML + Markdown | GitHub Copilot integration | `.github/instructions/*.md` |

### Build Specific Tool

```bash
# Build only for Kilo
promptosaurus build --tool kilo --agent architect

# Build only for Claude
promptosaurus build --tool claude --agent architect

# Build all agents for one tool
promptosaurus build --tool cline
```

### Build with Variant

```bash
# Build minimal variant (small, efficient)
promptosaurus build --variant minimal

# Build verbose variant (detailed, comprehensive)
promptosaurus build --variant verbose
```

### List Available Agents

```bash
promptosaurus list

# Output:
# Available Agents:
# - architect (minimal, verbose)
# - test (minimal, verbose)
# - code (minimal, verbose)
```

---

## Complete Examples

### Example 1: Simple Architect Agent (Kilo)

**Directory Structure:**
```
agents/
└── architect/
    ├── minimal/
    │   └── prompt.md
    └── verbose/
        └── prompt.md
```

**Create IR (Intermediate Representation):**

```bash
mkdir -p agents/architect/{minimal,verbose}
```

**File: `agents/architect/minimal/prompt.md`**
```markdown
---
name: architect
description: Design system architecture
---

You are a software architect. Your role is to design:
- Data models and database schemas
- Service boundaries and API contracts
- Deployment architecture and topologies
```

**File: `agents/architect/verbose/prompt.md`**
```markdown
---
name: architect
description: Design system architecture and data models
---

You are an expert software architect with 15+ years of experience. You specialize in:

**Core Competencies:**
- Distributed systems design
- Microservices architecture
- Database modeling and optimization
- Cloud infrastructure design
- API design and standards

**Your Design Process:**

1. **Requirements Analysis**
   - Understand business requirements
   - Identify scalability constraints
   - Plan for growth

2. **Component Design**
   - Define service boundaries
   - Design data models
   - Plan data flow

3. **Implementation Planning**
   - Document architecture
   - Plan deployment strategy
   - Identify risks and mitigations

Focus on creating systems that are scalable, maintainable, and cost-effective.
```

**Build:**
```bash
promptosaurus build --tool kilo --agent architect
```

**Generated File: `.kilo/agents/architect.md`**
```yaml
---
name: architect
description: Design system architecture
tools: []
skills: []
workflows: []
---

# Architect Agent

You are a software architect. Your role is to design:
- Data models and database schemas
- Service boundaries and API contracts
- Deployment architecture and topologies
```

---

### Example 2: Test Agent with Skills (Cline)

**Directory Structure:**
```
agents/
└── test/
    ├── minimal/
    │   ├── prompt.md
    │   └── skills.md
    └── verbose/
        ├── prompt.md
        └── skills.md
```

**File: `agents/test/minimal/prompt.md`**
```markdown
---
name: test
description: Write comprehensive tests
---

You are a test engineer. Write tests that:
- Cover all code paths
- Test edge cases and boundaries
- Use clear, descriptive names
```

**File: `agents/test/minimal/skills.md`**
```markdown
---
skills: ["unit-testing", "edge-case-analysis"]
---

## Testing Skills

1. **unit-testing** - Write focused unit tests
2. **edge-case-analysis** - Identify boundary conditions
```

**File: `agents/test/verbose/prompt.md`**
```markdown
---
name: test
description: Write comprehensive tests with coverage-first approach
---

You are an expert test engineer focused on test quality and coverage.

**Test Design:**
- Write tests that verify behavior, not implementation
- Use property-based testing for generative inputs
- Cover happy paths, error cases, and edge cases

**Coverage Goals:**
- Line coverage: 90%+
- Branch coverage: 80%+
- Mutation testing: 80%+ kill rate

**Test Organization:**
- Unit tests: Fast, isolated, mocked dependencies
- Integration tests: Multi-component, real or in-memory services
- E2E tests: Full user flows, real environment
```

**File: `agents/test/verbose/skills.md`**
```markdown
---
skills: ["unit-testing", "edge-case-analysis", "mutation-testing", "property-based-testing"]
---

## Testing Skills

1. **unit-testing** - Write focused unit tests with excellent coverage
2. **edge-case-analysis** - Identify and test boundary conditions
3. **mutation-testing** - Verify test quality with fault injection
4. **property-based-testing** - Generative testing with Hypothesis
```

**Build:**
```bash
promptosaurus build --tool cline --agent test
```

**Generated Section: `.clinerules`**
```markdown
# Test Agent

You are a test engineer. Write tests that:
- Cover all code paths
- Test edge cases and boundaries
- Use clear, descriptive names

## Skills

- **unit-testing** - use_skill unit-testing
- **edge-case-analysis** - use_skill edge-case-analysis
```

---

### Example 3: Code Agent (Claude JSON Format)

**Directory Structure:**
```
agents/
└── code/
    ├── minimal/
    │   └── prompt.md
    └── verbose/
        └── prompt.md
```

**File: `agents/code/minimal/prompt.md`**
```markdown
---
name: code
description: Implement features and fix bugs
---

You are a software engineer. Your role:
- Implement new features
- Fix bugs and defects
- Write clean, tested code
```

**Build:**
```bash
promptosaurus build --tool claude --agent code
```

**Generated File: `claude-agents.json`**
```json
[
  {
    "name": "code",
    "description": "Implement features and fix bugs",
    "system": "You are a software engineer. Your role:\n- Implement new features\n- Fix bugs and defects\n- Write clean, tested code",
    "tools": [],
    "instructions": ""
  }
]
```

**Use with Claude API:**
```python
import anthropic
import json

# Load agent configuration
with open("claude-agents.json") as f:
    agents = json.load(f)

code_agent = agents[0]  # First agent

# Use with Claude
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    system=code_agent["system"],
    messages=[
        {"role": "user", "content": "Implement a user authentication system"}
    ]
)

print(response.content[0].text)
```

---

### Example 4: Security Agent (Cursor Rules)

**Directory Structure:**
```
agents/
└── security/
    ├── minimal/
    │   └── prompt.md
    └── verbose/
        └── prompt.md
```

**File: `agents/security/minimal/prompt.md`**
```markdown
---
name: security
description: Review code for security vulnerabilities
---

You are a security engineer. Review code for:
- Injection vulnerabilities (SQL, command, etc.)
- Authentication/authorization issues
- Secrets leakage
- OWASP Top 10 violations
```

**Build:**
```bash
promptosaurus build --tool cursor --agent security
```

**Generated File: `.cursorrules`**
```markdown
# Security Agent

You are a security engineer. Review code for:
- Injection vulnerabilities (SQL, command, etc.)
- Authentication/authorization issues
- Secrets leakage
- OWASP Top 10 violations
```

---

### Example 5: Review Agent (GitHub Copilot)

**Directory Structure:**
```
agents/
└── review/
    ├── minimal/
    │   └── prompt.md
    └── verbose/
        └── prompt.md
```

**File: `agents/review/minimal/prompt.md`**
```markdown
---
name: review
description: Review code for quality and performance
---

You are a code reviewer. Focus on:
- Code quality and readability
- Performance optimization
- Test coverage
- SOLID principles
```

**Build:**
```bash
promptosaurus build --tool copilot --agent review
```

**Generated File: `.github/instructions/review.md`**
```yaml
---
name: review
description: Review code for quality and performance
applyTo:
  - model: code
---

# Review Agent

You are a code reviewer. Focus on:
- Code quality and readability
- Performance optimization
- Test coverage
- SOLID principles
```

---

## CLI Command Reference

### Initialize Project

```bash
promptosaurus init
```

Interactive setup wizard:
1. Select repository type (single-language or monorepo)
2. Configure language and runtime
3. Choose which tools to support
4. Generate initial configuration

### List Agents

```bash
promptosaurus list

# With verbose output
promptosaurus list --verbose

# Filter by agent
promptosaurus list architect
```

### Build Agents

```bash
# Build all agents for all tools
promptosaurus build

# Build specific agent
promptosaurus build --agent architect

# Build for specific tool
promptosaurus build --tool kilo

# Build with specific variant
promptosaurus build --variant minimal

# Build to specific output directory
promptosaurus build --output ./output/
```

### Validate Configuration

```bash
promptosaurus validate

# Checks for:
# - All required files present
# - Valid YAML/Markdown format
# - No orphaned files
# - Consistent naming
```

---

## Troubleshooting

### Problem: Command Not Found

```bash
# Error: promptosaurus: command not found
```

**Solution:**
```bash
# Verify installation
pip list | grep promptosaurus

# If not installed, install it
pip install promptosaurus

# If installed but not in PATH, use python -m
python -m promptosaurus.cli --version
```

### Problem: Missing Required Files

```bash
# Error: agents/architect/minimal/prompt.md not found
```

**Solution:**
```bash
# Create the file
mkdir -p agents/architect/minimal
touch agents/architect/minimal/prompt.md

# Add minimal content
cat > agents/architect/minimal/prompt.md << 'EOF'
---
name: architect
description: Design system architecture
---

You are a software architect.
EOF
```

### Problem: Invalid YAML Frontmatter

```bash
# Error: YAMLError: expected '<document start>'
```

**Solution:**
```bash
# Check file starts with ---
head -1 agents/architect/minimal/prompt.md

# Should show: ---
# If missing, add it at the beginning of file
```

### Problem: Tool-Specific Issues

**For Kilo:**
```bash
# Verify YAML is valid
python -c "import yaml; yaml.safe_load(open('.kilo/agents/architect.md'))"
```

**For Cline:**
```bash
# Check file exists and is readable
cat .clinerules | head -20
```

**For Claude:**
```bash
# Verify JSON is valid
python -c "import json; json.load(open('claude-agents.json'))"
```

**For Cursor:**
```bash
# Check .cursorrules is readable
cat .cursorrules | head -10
```

**For Copilot:**
```bash
# Check GitHub instructions file
cat .github/instructions/architect.md | head -20
```

### Problem: Build Slow or Stuck

```bash
# Run with verbose output
promptosaurus build --verbose

# Check for file system issues
ls -la agents/
du -sh agents/
```

### Problem: Can't Find Generated Files

```bash
# Search for generated files
find . -name "*.md" -path "./.kilo/*"
find . -name "*.rules" -path "./.cursor/*"
find . -name "*.json" -name "*agent*"

# Check all possible locations
ls -la .kilo/agents/
cat .clinerules | head -5
ls -la .github/instructions/
```

---

## Next Steps

After getting started:

1. **Read the Full Documentation**
   - [PHASE2A_RELEASE_NOTES.md](./PHASE2A_RELEASE_NOTES.md) - What's new in Phase 2A
   - [BUILDER_API_REFERENCE.md](./BUILDER_API_REFERENCE.md) - API documentation
   - [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Migrate from old system

2. **Explore Advanced Features**
   - Skills and workflows
   - Subagent delegation
   - Variant selection (minimal vs verbose)
   - Custom component composition

3. **Create More Agents**
   - Test agent (for testing-first development)
   - Review agent (for code review)
   - Debug agent (for debugging tasks)
   - Architect agent (for system design)

4. **Integrate with Your Workflow**
   - Add `promptosaurus build` to your CI/CD
   - Generate agents on pre-commit hook
   - Commit generated files for reproducibility

---

## Quick Reference

| Task | Command |
|------|---------|
| Install | `pip install promptosaurus` |
| List agents | `promptosaurus list` |
| Build all | `promptosaurus build` |
| Build Kilo | `promptosaurus build --tool kilo` |
| Validate | `promptosaurus validate` |
| Get help | `promptosaurus --help` |

---

## Support

- **Issues:** Report bugs on GitHub
- **Questions:** Ask in GitHub Discussions
- **Documentation:** See docs/ directory in repository
- **Examples:** See examples/ directory

---

**Ready to get started? Create your first agent directory and run `promptosaurus build`!** 🚀
