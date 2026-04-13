# GitHub Copilot Instructions Example

This example shows the output from the **CopilotBuilder** for GitHub Copilot integration.

## What's Included

- **`copilot-instructions.md`** - Complete Copilot instructions file with YAML frontmatter and markdown sections

## File Format

GitHub Copilot uses a markdown file with YAML frontmatter:

```markdown
---
applyTo:
  - model: code
---

# Agent Name

[Instructions and guidance]

## Section

[Detailed instructions]
```

The `applyTo` field controls which Copilot model receives these instructions.

## Installation

Place the instructions file in your GitHub repository:

```bash
# Create the instructions directory
mkdir -p .github/instructions

# Copy the example
cp examples/copilot/copilot-instructions.md .github/instructions/code.md
```

Copilot will automatically load instructions from `.github/instructions/*.md` when you use GitHub Codespaces or Copilot in GitHub.

## File Sections Explained

### YAML Frontmatter

```yaml
---
applyTo:
  - model: code
---
```

The `applyTo` field specifies when these instructions apply:
- `model: code` - Apply to Copilot in Code mode
- Other models: `chat`, `suggest`, etc.

### Main Heading

The top-level heading names the instruction set:
```markdown
# Copilot Code Agent Instructions
```

### System Behavior

Introduction explaining the AI's role:
```markdown
You are an expert code generation assistant. Write clean,
well-documented Python code following SOLID principles.
```

### Subsections

Organized sections for different aspects:
- Code Quality Standards
- Workflow
- Available Tools
- SOLID Principles
- Best Practices
- Code Review Focus Areas

## Customization Guide

### Change the Copilot Model

Edit `applyTo` to target different models:

```yaml
---
applyTo:
  - model: code        # Instructions for code mode
  - model: chat        # Also apply to chat mode
---
```

### Change the Role

Update the main heading and introduction:

```markdown
# Copilot Test Writing Instructions

You are an expert test engineer. Write comprehensive,
well-structured tests with high coverage...
```

### Add Language-Specific Rules

Add a section for your primary language:

```markdown
## Python-Specific Standards

- Use type hints on all public functions
- Follow PEP 8 style guide
- Minimum Python version: 3.9+
- Use pytest for testing
```

### Customize Code Examples

Include patterns specific to your project:

```markdown
## Function Structure

In this project, use this pattern:

```python
def function_name(param1: str) -> bool:
    """Clear docstring.
    
    Args:
        param1: Parameter description
        
    Returns:
        True if successful
    """
    # Implementation
    pass
```
```

### Add Project-Specific Guidance

Reference your project's conventions:

```markdown
## This Project

- We use pytest for testing
- All public functions must be documented
- Type hints are required
- Minimum 80% test coverage
- Follow conventions in /docs/CODING_STANDARDS.md
```

## Common Patterns

### Code Review Instructions

```markdown
---
applyTo:
  - model: code
---

# Copilot Code Review Instructions

You are an expert code reviewer providing constructive feedback.

## Review Checklist

- [ ] Code follows project style guide
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] Test coverage is adequate
- [ ] Documentation is clear
- [ ] Performance is acceptable

## Feedback Style

- Be constructive and respectful
- Explain the "why" behind suggestions
- Acknowledge good code
- Prioritize critical issues
```

### Test Writing Instructions

```markdown
---
applyTo:
  - model: code
---

# Copilot Test Writing Instructions

You are an expert test engineer writing comprehensive tests.

## Test Patterns

- Unit tests: Test single functions in isolation
- Integration tests: Test components together
- Edge cases: Empty, null, boundary values
- Error cases: Invalid inputs, exceptions

## Test Naming

test_{function}_{scenario}_{expected}

Example:
- test_parse_json_with_valid_input_returns_dict
- test_parse_json_with_invalid_input_raises_error
```

### Documentation Instructions

```markdown
---
applyTo:
  - model: code
---

# Copilot Documentation Instructions

You are a technical writer generating clear documentation.

## Documentation Standards

- Include practical examples for every feature
- Explain the "why" not just the "how"
- Use consistent terminology
- Cross-reference related topics
- Add troubleshooting sections

## Example Format

### Feature Name

Brief description of what it does.

Usage:

```code
example_code_here()
```

Output:
```
expected_output
```
```

## File Placement

Store instructions in `.github/instructions/`:

```
your-repository/
├── .github/
│   └── instructions/
│       ├── code.md                ← Main code instructions
│       ├── test.md                ← Test writing instructions
│       ├── documentation.md       ← Documentation instructions
│       └── review.md              ← Code review instructions
├── src/
├── tests/
├── README.md
└── ...
```

Each file should have its own `applyTo` configuration.

## Multiple Models

To apply instructions to multiple Copilot models:

```yaml
---
applyTo:
  - model: code
  - model: chat
---

# Copilot Instructions (Code and Chat)

These instructions apply to both code and chat modes.
```

## Versioning

Instructions are loaded from GitHub, so:
- Push changes to trigger updates
- GitHub users get instructions immediately (on next activation)
- Include version notes if making breaking changes:

```markdown
## Version History

**v2.0** (2024-03-15)
- Added Python 3.12 syntax guidelines
- Updated testing standards

**v1.0** (2024-01-01)
- Initial release
```

## Editing Tips

### Be Clear and Specific

Instead of:
```markdown
Write good tests.
```

Better:
```markdown
Write tests that:
- Cover the happy path and error cases
- Have descriptive names (test_feature_scenario_result)
- Achieve minimum 80% coverage
- Can run independently in any order
```

### Use Examples

Instead of:
```markdown
Use type hints.
```

Better:
```markdown
Use type hints:

Good:
```python
def process(data: List[str]) -> Optional[dict]:
    pass
```

Bad:
```python
def process(data):
    pass
```
```

### Reference External Docs

Link to existing standards:

```markdown
## Code Standards

For detailed standards, see:
- [CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md)
- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- [API_DESIGN.md](../../docs/API_DESIGN.md)
```

## Troubleshooting

### Instructions not loading

**Check:**
1. File is in `.github/instructions/` directory
2. Filename ends with `.md`
3. YAML frontmatter is valid (see example above)
4. You're using GitHub Copilot in GitHub or Codespaces

**Verify:**
```bash
# File should exist
ls -la .github/instructions/code.md

# YAML syntax should be valid
head -5 .github/instructions/code.md  # Should show --- markers
```

### Copilot not following instructions

**Check:**
1. Instructions are clear and specific
2. Instructions don't contradict each other
3. Instructions are in plain language (not too complex)
4. Copilot has been restarted

**Improve:**
- Make instructions shorter and more direct
- Provide concrete examples
- Separate concerns into different sections
- Be specific about what to do, not what not to do

### Too much content

If instructions are too long:
1. Focus on most critical guidance (max ~200 lines)
2. Move detailed standards to external docs and reference them
3. Use examples instead of lengthy explanations
4. Organize with clear section headings

## Best Practices

### Keep It Focused

Each instructions file should have a clear purpose:
- code.md - General code generation
- test.md - Test writing specifics
- review.md - Code review guidelines
- documentation.md - Doc generation

### Use Concrete Examples

Include real code patterns from your project:

```markdown
## Naming Convention

Our project uses snake_case for functions:

```python
def process_user_data(user_id: str) -> dict:
    pass
```
```

### Version Your Instructions

Add version notes for tracking:

```markdown
## Instructions Version

**Current:** v2.1 (2024-03-20)
- Based on Python 3.11+
- pytest framework
- Type hints required
```

### Reference Your Standards

Link to existing documentation:

```markdown
For complete coding standards, see:
- [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
```

## Integration with CI/CD

Your instructions should align with your CI checks:

```markdown
## Testing Requirements

All code must pass:
- pytest (unit and integration tests)
- pyright (type checking)
- ruff (linting and formatting)
- 80%+ coverage

These same checks run in CI, so following these instructions
ensures your code will pass automated checks.
```

## Next Steps

1. **Copy the example** to `.github/instructions/code.md`
2. **Edit** to match your project's standards
3. **Review** for clarity and completeness
4. **Commit and push** to make it live
5. **Test** with Copilot to ensure it works

## For More Information

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Builder Documentation](../../docs/BUILDERS.md)
- [Agent Configuration Guide](../../docs/AGENT_CONFIG.md)
