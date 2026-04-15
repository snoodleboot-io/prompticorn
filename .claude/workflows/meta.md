# Meta-Workflow (Minimal)

## Purpose
Define systematic approaches to creating, documenting, testing, and iterating on workflows themselves.

## Steps

### 1. Define Workflow Scope
- Identify the problem the workflow solves
- Define entry conditions (when to use this workflow)
- Define exit conditions (success criteria)
- List prerequisites (tools, permissions, knowledge required)

### 2. Identify Workflow Steps
- Break the process into discrete, actionable steps
- Order steps by dependency (what must happen first)
- Identify decision points and branching logic
- Note which steps can be parallelized

### 3. Document Workflow
- Write minimal version (25-50 lines, essential steps only)
- Write verbose version (200-400 lines, full detail with examples)
- Include YAML frontmatter with metadata
- Add real examples (not placeholders)

### 4. Test Workflow
- Walk through workflow with real scenario
- Identify unclear steps or missing information
- Test all decision branches
- Verify exit conditions are achievable

### 5. Iterate and Improve
- Gather feedback from workflow users
- Identify common failure points
- Add clarifications or missing steps
- Version the workflow (increment version field)