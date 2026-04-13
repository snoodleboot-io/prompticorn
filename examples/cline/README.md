# Cline AI Rules Example

This example shows the output from the **ClineBuilder** for a simple "code" agent.

## What's Included

- **`.clinerules`** - Complete Cline AI configuration file in markdown format

## File Format

Cline uses a single `.clinerules` markdown file (no YAML frontmatter):

```markdown
# {Agent Name} Rules

[Agent role and responsibilities]

## Key Section

[Guidelines and constraints]

## Another Section

[More instructions]
```

The file is plain markdown - simple to read and edit.

## Installation

Place the rules file in your project root:

```bash
# Copy the example to your project root
cp examples/cline/.clinerules .clinerules
```

Cline will automatically load `.clinerules` from your project root when you start the AI.

## File Sections Explained

### Header

The top-level heading identifies the agent:
```markdown
# Code Rules
```

### Role & Responsibilities

Brief description of what the agent does:
```markdown
You are an expert code generation assistant.
Write clean, well-documented Python code following SOLID principles.
```

### Subsections

Organize rules into logical sections:
- Code Quality Standards
- Workflow
- Tools
- Key Principles

Each section uses `##` level headings.

## Customization Guide

### Change the Agent Name

Edit the top-level heading:

```markdown
# Test Writer Rules  # Changed from "Code Rules"
```

Update the role description:
```markdown
You are an expert test engineer...
```

### Add Rules for Your Language

For Python:
```markdown
## Python Standards

- Use type hints on all public functions
- Follow PEP 8 style guide
- Use pytest for testing
- Minimum Python version: 3.9+
```

For TypeScript:
```markdown
## TypeScript Standards

- Strict mode enabled in tsconfig.json
- No `any` types without explicit justification
- Use interfaces for object shapes
- ESLint and Prettier for formatting
```

### Create Domain-Specific Rules

Example for a documentation agent:

```bash
cp examples/cline/.clinerules .clinerules
```

Edit:
```markdown
# Documentation Rules

You are a technical writer specializing in API documentation.

## Documentation Standards

- Clear examples for every feature
- Consistent formatting across docs
- Explain the "why" not just the "how"
- Link to related topics

## Workflow

1. Read the code thoroughly
2. Understand the purpose and usage
3. Write clear, concise documentation
4. Add practical examples
5. Review for clarity and accuracy

## Tools

- read: Study source code and existing docs
- write: Create or update documentation
- execute: Generate examples
```

### Add Workflow Sections

Cline works best with explicit workflows:

```markdown
## Code Review Workflow

1. **Read**: Understand the changed files
2. **Analyze**: Check for bugs and issues
3. **Verify**: Check test coverage
4. **Feedback**: Provide actionable comments
5. **Approve**: Only if all checks pass
```

### Define Tool Usage

Be explicit about which tools to use and when:

```markdown
## Tools

The following tools are available:

- **read**: Use to understand code structure and existing patterns
- **write**: Use to create or modify files
- **execute**: Use to run tests and verify changes
```

## Common Patterns

### Python Development Agent

```markdown
# Python Developer Rules

You are an expert Python developer following best practices.

## Code Style

- Follow PEP 8 and the project's conventions
- Use type hints on all public functions
- Write clear, descriptive variable names

## Quality Standards

- Minimum 80% code coverage
- No circular imports
- Use dataclasses for data containers
- Use `Optional[T]` or `T | None` for nullable types

## Testing

- Use pytest framework
- Test names: test_{function}_{scenario}_{expected}
- Include both happy path and error cases
```

### Code Reviewer Agent

```markdown
# Code Reviewer Rules

You provide expert code reviews focusing on quality and maintainability.

## Review Checklist

- Does the code follow the project's style guide?
- Are there any obvious bugs or logic errors?
- Is error handling appropriate?
- Are there sufficient tests?
- Is the code maintainable?

## Feedback Style

- Be constructive and respectful
- Explain the "why" behind suggestions
- Acknowledge good code
- Prioritize critical issues
```

### Architect/Designer Agent

```markdown
# Architecture Assistant Rules

You help design scalable, maintainable systems.

## Design Principles

- Apply SOLID principles
- Consider scalability from the start
- Document trade-offs
- Favor simplicity over complexity

## Workflow

1. Understand the requirements
2. Identify constraints and risks
3. Propose multiple approaches
4. Evaluate trade-offs
5. Document the decision
```

## Editing Tips

### Use Clear, Direct Language

Good:
```markdown
Always use type hints on public functions.
```

Not so good:
```markdown
You might consider possibly using type hints when appropriate.
```

### Provide Examples

Instead of:
```markdown
Use descriptive function names.
```

Better:
```markdown
Use descriptive function names:
- Good: parse_json_config()
- Bad: parse()
```

### Be Specific

Instead of:
```markdown
Write good tests.
```

Better:
```markdown
Write tests that:
- Test the happy path and error cases
- Have descriptive names explaining what's tested
- Achieve minimum 80% code coverage
- Are independent and can run in any order
```

## File Placement

The `.clinerules` file should be in your project root:

```
your-project/
├── .clinerules          ← This file
├── src/
├── tests/
├── README.md
└── ...
```

## Cline Behavior

When Cline reads `.clinerules`:
1. Loads the file at startup
2. Incorporates rules into its system prompt
3. Follows the guidelines throughout the conversation
4. References the rules when making decisions

## Troubleshooting

### Cline not loading rules

**Check:**
1. File is named `.clinerules` (note the dot prefix)
2. File is in the project root directory
3. Cline has been restarted after adding the file

**Verify:**
```bash
# File should exist
ls -la .clinerules

# File should be readable
cat .clinerules | head -5
```

### Rules not being followed

**Check:**
1. Rules are clear and specific
2. Rules don't contradict each other
3. Rules are in plain language (not overly complex)

**Improve:**
- Make rules shorter and more direct
- Provide concrete examples
- Separate concerns into different sections

### Too many rules

If Cline is slow or confused:
1. Keep file to ~100 lines maximum
2. Focus on most critical rules
3. Remove redundant sections
4. Use bold for emphasis instead of more text

## Example Variations

### Minimal Rules

For quick setup:

```markdown
# Code Rules

You are an expert code generation assistant.

## Standards

- Use type hints
- Write tests
- Follow PEP 8
- Document clearly

## Tools

- read: Understand code
- write: Create files
- execute: Run tests
```

### Comprehensive Rules

For detailed governance:

```markdown
# Code Rules

[Detailed role description]

## Code Quality Standards

[Sub-headings for each area]

## Workflow

[Step-by-step process]

## Tools

[Detailed tool descriptions]

## Key Principles

[Core values]

## Language-Specific Guidelines

[Standards per language]

## Testing Standards

[Testing requirements]

## Documentation Standards

[Docs requirements]
```

## Next Steps

1. **Copy the example** to your project root as `.clinerules`
2. **Edit** the content to match your needs
3. **Review** for clarity and completeness
4. **Test** with Cline to ensure rules are followed
5. **Iterate** based on how Cline behaves

## For More Information

- [Cline Documentation](https://github.com/cline/cline)
- [Builder Documentation](../../docs/BUILDERS.md)
- [Agent Configuration Guide](../../docs/AGENT_CONFIG.md)
