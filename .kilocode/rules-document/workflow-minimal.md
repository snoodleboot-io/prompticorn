<!-- path: promptosaurus/.kilocode/rules-document/workflow-minimal.md -->
# Documentation Workflow - Minimal Version

**Metadata:**
- languages: [all]
- subagents: [document/api, document/strategy]
- estimated_time: 1-4 hours
- complexity: low-medium

## Documentation Checklist (Quick Reference)

### 1. Overview (15 min)
- [ ] Write one sentence: what does this do?
- [ ] Describe the primary use case
- [ ] Note any prerequisites or dependencies

### 2. Public API/Interface (30 min)
- [ ] List all exported functions, classes, or endpoints
- [ ] Document parameters, return types, errors
- [ ] Include one realistic example for each
- [ ] Note any important constraints or gotchas

### 3. Usage Examples (30 min)
- [ ] Write 2-3 realistic usage examples
- [ ] Examples must actually run (test them!)
- [ ] Include both happy path and error handling
- [ ] Explain what each example demonstrates

### 4. Troubleshooting Section (15 min)
- [ ] List common errors users encounter
- [ ] Provide fix for each error
- [ ] Include diagnostic steps
- [ ] Link to relevant sections

### 5. Verification (15 min)
- [ ] Read all examples and run them
- [ ] Check that documentation matches code
- [ ] Verify all links work
- [ ] Ask someone unfamiliar to read it

## Documentation Types

**API Reference:** What functions/endpoints exist, parameters, returns  
**User Guide:** How to accomplish common tasks  
**Examples:** Working code samples  
**Troubleshooting:** Common problems and solutions  
**Architecture:** How components fit together  

## Critical Rules

- ✓ Comment the WHY, never the WHAT
- ✓ Examples must be real and runnable
- ✓ Match documentation to actual code
- ✓ Remove outdated documentation completely
- ✗ Don't include marketing copy or aspirations

## Abort Criteria

Stop and ask for help if:
- Documentation conflicts with actual code
- Examples don't run without changes
- Core functionality unclear in code itself

---

**Total Steps: 5 | Estimated Lines: 26 | Complexity: Quick checklist**
