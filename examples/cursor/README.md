# Cursor IDE Rules Example

This example shows the output from the **CursorBuilder** for Cursor IDE integration.

## What's Included

- **`.cursorrules`** - Complete Cursor IDE rules file in markdown format

## File Format

Cursor uses a plain `.cursorrules` markdown file (no YAML frontmatter or metadata):

```markdown
# Title

Description and role...

## Section Name

Rules and guidelines...

## Another Section

More instructions...
```

The file is loaded automatically by Cursor when you open a project.

## Installation

Place the rules file in your project root:

```bash
# Copy the example to your project root
cp examples/cursor/.cursorrules .cursorrules
```

Cursor will automatically detect and load `.cursorrules` from your project root.

## File Sections Explained

### Main Title

The opening describes the agent's role:
```markdown
# Code Generation Rules

You are an expert code generation assistant...
```

### Core Constraints

Critical rules that must always be followed:
```markdown
## Core Constraints

- Type hints required on all public functions
- Every module must have a docstring
- Minimum 80% test coverage
```

These are constraints Cursor will rigorously enforce.

### Subsections

Organize rules into logical areas:
- Code Quality Standards
- Workflow
- SOLID Principles
- Python Best Practices
- File Naming Convention
- Common Patterns
- Before Starting Work

## Customization Guide

### Change the Agent Role

Edit the opening section:

```markdown
# Test Writer Rules

You are an expert test engineer. Write comprehensive,
well-structured tests with high coverage...
```

Update the rest accordingly.

### Add Language-Specific Rules

Expand the standards section for your language:

```markdown
## TypeScript Standards

- Use strict mode
- No `any` types without justification
- Interfaces for object shapes
- ESLint and Prettier configured
```

### Define Your Workflow

Create a specific workflow section:

```markdown
## Code Implementation Workflow

1. **Read**: Study relevant source files
   - Understand existing patterns
   - Check related code and tests
   - Identify conventions

2. **Plan**: Outline approach
   - Identify needed classes/functions
   - Determine dependencies
   - Consider edge cases

3. **Write**: Implement following patterns
   - Match existing code style
   - Include complete docstrings
   - Add type hints immediately

4. **Test**: Verify thoroughly
   - Write tests alongside code
   - Achieve 80%+ coverage
   - Test edge cases

5. **Document**: Add final touches
   - Inline comments for complex logic
   - Update related docs
   - Verify type checking passes
```

### Customize Code Patterns

Include your actual code patterns:

```markdown
## Function Structure

All functions in this project follow this pattern:

```python
def my_function(param: str) -> bool:
    """Summary line.
    
    Extended description...
    
    Args:
        param: What this parameter means
        
    Returns:
        What gets returned
    """
    # Implementation
```
```

### Add Project-Specific Rules

```markdown
## This Project's Standards

- Python 3.11+ only
- pytest framework
- pyright for type checking
- ruff for linting
- Minimum 80% coverage
- See docs/CODING_STANDARDS.md for details
```

## Common Patterns

### Python Development Rules

```markdown
# Python Developer Rules

You are an expert Python developer.

## Core Constraints

- Type hints required on all public functions
- Every module/class/function has a docstring
- No generic Exception - use specific types
- Minimum 80% test coverage
- No circular imports

## Testing

- Use pytest
- Test names: test_{function}_{scenario}_{result}
- Test both success and error paths
- Mock only external dependencies

## Code Style

- Follow PEP 8
- snake_case for functions/variables
- PascalCase for classes
- UPPER_SNAKE for constants (discouraged - use config)
```

### Code Review Rules

```markdown
# Code Review Rules

You are an expert code reviewer.

## Core Constraints

- All feedback must be constructive
- Explain the "why" behind suggestions
- Prioritize critical issues first
- Acknowledge good code

## Review Checklist

- Functionality: Does it do what it should?
- Correctness: Any bugs or missed cases?
- Style: Does it follow conventions?
- Performance: Any obvious inefficiencies?
- Testing: Is coverage adequate?
- Documentation: Clear docstrings?

## Feedback Pattern

1. Acknowledge what works
2. Explain the issue clearly
3. Suggest specific fix
4. Provide example if helpful
```

### Architecture Rules

```markdown
# Architecture Rules

You design scalable, maintainable systems.

## Core Constraints

- Apply SOLID principles
- Minimize coupling
- Maximize cohesion
- Document trade-offs

## Design Process

1. Understand requirements thoroughly
2. Identify constraints and risks
3. Propose multiple approaches
4. Evaluate trade-offs explicitly
5. Document the decision

## Questions to Ask

- Is this extensible for future needs?
- Can components be tested independently?
- Are dependencies well-managed?
- Is complexity justified?
```

## File Placement

The `.cursorrules` file belongs in your project root:

```
your-project/
├── .cursorrules         ← This file
├── src/
├── tests/
├── docs/
├── README.md
└── ...
```

Cursor searches upward through parent directories for `.cursorrules`, so placing it in the project root makes it available to all files.

## Editing Tips

### Be Specific, Not Vague

Instead of:
```markdown
Write good code.
```

Better:
```markdown
Write code that:
- Uses type hints on all public functions
- Includes complete docstrings
- Achieves 80%+ test coverage
- Passes pyright strict mode
```

### Use Examples

Show don't tell:

```markdown
## Naming Convention

Use snake_case for functions:

```python
# Good
def parse_user_config(path: str) -> dict:
    pass

# Bad
def parseUserConfig(path):
    pass
```
```

### Organize Logically

Group related rules together:

```markdown
## Type System

### Required Type Hints
- All public functions
- Function parameters
- Function return values

### Type Checking
- Must pass pyright strict mode
- No `Any` without justification
- Use specific exception types
```

### Keep It Focused

Long rules files are harder to follow. Aim for ~100-150 lines.

Focus on most important constraints:
- Type hints (high impact)
- Testing (prevents bugs)
- Documentation (maintains clarity)
- Style (ensures consistency)

## How Cursor Uses Rules

When you work in a Cursor project:
1. Cursor loads `.cursorrules` at startup
2. Rules are incorporated into the AI context
3. AI follows rules throughout the conversation
4. Rules guide code generation and editing

You can also:
- Reference rules in prompts: "Follow the patterns in .cursorrules"
- Update rules to change behavior without restarting
- Include rules in custom instructions

## Troubleshooting

### Rules not loading

**Check:**
1. File is named `.cursorrules` (dot prefix)
2. File is in project root directory
3. Cursor has been restarted after adding file

**Verify:**
```bash
# File should exist
ls -la .cursorrules

# Should be readable
cat .cursorrules | head -10
```

### Cursor not following rules

**Check:**
1. Rules are clear and specific
2. Rules don't contradict each other
3. Rules aren't overly complex

**Improve:**
- Make rules more direct and concise
- Add concrete examples
- Remove redundant rules
- Separate concerns into sections

### Rules are too long

If Cursor seems slow or confused:
1. Reduce file to max ~150 lines
2. Focus on critical rules only
3. Remove explanations (rules should be obvious)
4. Use bold/emphasis instead of extra text

## Best Practices

### Keep Core Constraints Front and Center

```markdown
## Core Constraints

[Most critical rules - 5-10 lines max]

[Rest of detailed rules]
```

### Link to Detailed Docs

```markdown
## Code Standards

For comprehensive standards, see:
- [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
```

### Version Your Rules

Track changes:

```markdown
## Cursor Rules Version

**Current:** v2.1 (Updated: 2024-03-20)

**Changes:**
- v2.1: Added TypeScript standards
- v2.0: Restructured for clarity
- v1.0: Initial release
```

### Make Rules Observable

Rules should result in code that's clearly different:

❌ Poor:
```
Be thoughtful about performance.
```

✅ Good:
```
- Use appropriate data structures (set vs list)
- Cache expensive computations
- Document performance assumptions
- Profile before optimizing
```

## Integration with CI/CD

Align rules with automated checks:

```markdown
## Testing Requirements

All code must pass:
- pytest unit tests (80%+ coverage)
- pyright type checking (strict mode)
- ruff linting and formatting

These checks run in CI, so following these rules
ensures your code will pass automated validation.
```

## Using with Custom Instructions

Reference `.cursorrules` in custom instructions:

```
Follow the patterns defined in .cursorrules for this project.
Ensure all code meets the Core Constraints.
```

## Example Variations

### Minimal Rules

For quick onboarding:

```markdown
# Code Rules

You are an expert developer.

## Core Constraints

- Type hints on public functions
- Docstrings on all modules/classes
- 80%+ test coverage
- Specific exception types

## Workflow

1. Read existing code
2. Understand patterns
3. Write clean code
4. Test thoroughly
```

### Comprehensive Rules

For detailed governance:

```markdown
# Code Rules

[Full introduction]

## Core Constraints

[Critical rules]

## Code Quality

[Detailed standards per area]

## Workflow

[Step-by-step process]

## SOLID Principles

[Explanation of each]

## Python Standards

[Language-specific guidance]

## Common Patterns

[Code examples]

## Testing

[Testing standards]

## Before Starting

[Pre-implementation checklist]
```

## Next Steps

1. **Copy the example** to your project root as `.cursorrules`
2. **Edit** the content to match your project
3. **Review** for clarity and completeness
4. **Test** with Cursor to ensure it's being followed
5. **Iterate** based on how Cursor behaves

## For More Information

- [Cursor Documentation](https://cursor.sh/docs)
- [Cursor Rules Guide](https://cursor.sh/docs/context/cursorrules)
- [Builder Documentation](../../docs/BUILDERS.md)
- [Agent Configuration Guide](../../docs/AGENT_CONFIG.md)
