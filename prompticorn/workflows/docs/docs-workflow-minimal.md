---
name: docs-workflow
languages: [all]
subagents: [document/api, document/readme, code/feature]
version: "1.0"
---

# Documentation Workflow (Minimal)

## Step 1: Write Overview

- Create high-level summary explaining what the project/feature does in 2-3 sentences
- Document the primary use case and target audience
- List key concepts or terminology users need to understand

## Step 2: Document Public API

- List all public functions, classes, and methods with type signatures
- Document parameters with types, required/optional status, and default values
- Document return values with types and possible error conditions
- Add code examples for each public API showing typical usage

## Step 3: Add Examples

- Create "Hello World" example showing minimal working code
- Add 3-5 real-world examples covering common use cases
- Include expected output for each example
- Provide complete, runnable code snippets (not fragments)

## Step 4: Troubleshooting Section

- List 5-10 most common errors users encounter
- For each error: exact error message, cause, and solution
- Add FAQ section answering recurring questions from support tickets
- Include debugging tips and how to enable verbose logging

## Step 5: Verify Examples Work

- Copy each code example into a test file and run it
- Verify output matches documented expected output
- Test examples against all supported versions (if multiple)
- Fix any examples that fail or produce unexpected results

## Step 6: Review and Publish

- Run spell checker and grammar checker on all documentation
- Verify all links work (use link checker tool)
- Check that code examples follow code style conventions
- Deploy documentation to hosting platform and verify rendering
