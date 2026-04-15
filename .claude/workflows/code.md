# Code Implementation Workflow (Minimal)

## Step 1: Plan Before Coding

- Restate the goal in your own words
- List all files that will need changes
- Identify external dependencies or API changes
- Flag assumptions you're making
- Get confirmation before writing code

## Step 2: Read Existing Code

- Read the relevant source files first
- Understand existing patterns in the same layer
- Check conventions documentation
- Identify similar implementations to follow
- Never assume file contents without reading

## Step 3: Follow Conventions

- Match naming patterns from existing code
- Use error handling style from conventions
- Follow file structure and organization rules
- Type all function signatures explicitly
- Use language idioms (not patterns from other languages)

## Step 4: Implement Incrementally

- Write one file at a time
- Run tests after each file
- Commit small working changes
- Add inline comments for WHY, not WHAT
- Use TODO comments for judgment calls

## Step 5: Verify and Document

- Run full test suite
- Check for new warnings or linter errors
- List any follow-up work created
- Document any tech debt introduced
- Note tests that should be added