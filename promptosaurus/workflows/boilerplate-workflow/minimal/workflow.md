---
languages: ["python", "typescript", "javascript"]
subagents: ["code"]
---

# Boilerplate Generation Workflow (Minimal)

## 1. Identify Pattern
Recognize repetitive structure that needs templating:
- Look for files with similar structure but different names/params
- Common patterns: models, controllers, services, repositories, tests
- Document the pattern: What stays the same? What varies?

## 2. Read Existing Examples
Before generating, read 2-3 existing files from same layer:
```bash
# Find existing files of same type
find src/ -name "*_controller.py" | head -3
find src/ -name "*Service.ts" | head -3
```
- Note naming conventions (snake_case, PascalCase)
- Note import patterns and dependencies
- Note structure (class-based, functional)

## 3. Create Template Structure
Generate signatures and structure only, NO logic:
- Class/function definitions with type signatures
- Method stubs with return types
- Constructor/initialization patterns
- Use `# TODO: implement` or `throw new Error('Not implemented')` placeholders

## 4. Parameterize Variables
Identify what needs to be replaced:
- Entity/resource name (User, Product, Order)
- Field names and types
- API endpoints or database tables
- Related entities and foreign keys

## 5. Generate Companion Test File
Create test skeleton alongside implementation:
- Mirror implementation file structure
- Generate test stubs for each public method
- Include setup/teardown patterns from existing tests
- Add `# TODO: write test` placeholders

## 6. Verify Against Conventions
Check generated code matches project standards:
- Follows Core Conventions naming rules
- Uses correct file/folder structure
- Imports follow project patterns
- All types are properly declared (no `any` or missing types)

## 7. Document Usage
Provide brief guide for using the boilerplate:
- What needs to be filled in (TODOs)
- What NOT to change (framework hooks, base methods)
- Related files that may need updates (routers, exports)
