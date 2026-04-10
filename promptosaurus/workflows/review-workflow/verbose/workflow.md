---
name: review-workflow
description: Comprehensive code review process
languages: [all]
subagents: [review/code, review/security, review/compliance, enforcement/code-style, architecture/design]
steps:
  - Review code against conventions
  - Check test coverage and quality
  - Verify error handling patterns
  - Validate security and access control
  - Audit API contracts
  - Check documentation
  - Performance and scalability review
  - Compliance validation
  - Approve or request changes
  - Document review findings
---

## Code Review Workflow - Verbose

### Step 1: Review code against conventions

Check that code follows core-conventions.md and matches the patterns established elsewhere in the codebase.

**Check against:**
- File and folder naming conventions (snake_case vs camelCase)
- Variable and function naming patterns
- Class organization (one class per file)
- Import/export patterns
- Error handling style
- Async/await patterns
- Type annotations and strictness
- Code style (formatting, indentation)

**For deviations:**
- MUST FIX: Violations that confuse maintainers or break established patterns
- NIT: Minor preference differences

**Output:** List of convention violations and required fixes.

### Step 2: Check test coverage and quality

Verify the code has appropriate test coverage and the tests properly validate behavior.

**Coverage targets (language-specific):**
- Python: Line 80%, Branch 70%, Function 90%
- TypeScript: Line 90%, Branch 80%, Function 95%

**Test quality checks:**
- Tests validate behavior, not implementation details
- Edge cases are covered (empty, null, boundary values)
- Error paths are tested
- Mocking is appropriate (only external dependencies)
- Test names describe what is being tested
- No flaky or intermittent tests

**Tools:**
- Python: pytest with pytest-cov for coverage measurement
- TypeScript: vitest or Jest with coverage reporting

**Output:** Coverage report and list of missing test cases.

### Step 3: Verify error handling patterns

Ensure errors are properly caught, logged, and handled with appropriate context.

**Check:**
- No generic Exception/Error catches
- Errors include context (what failed and why)
- Errors are logged at the boundary (where handled, not where thrown)
- Typed errors used instead of generic Error
- Async errors are properly awaited
- Database errors include query context
- Network errors include URL/endpoint
- Validation errors include field names and constraints

**Patterns:**
- Python: Custom exception hierarchies, logging context
- TypeScript: Typed error unions, proper error propagation

**Output:** List of error handling improvements needed.

### Step 4: Validate security and access control

Check for security vulnerabilities, secrets management, and proper access control.

**Security checks:**
- No hardcoded secrets or credentials in code
- Environment variables used for all sensitive configuration
- Input validation on all user-provided data
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- CSRF protection where applicable
- Authentication/authorization checks present
- Rate limiting on sensitive endpoints
- Proper CORS headers
- HTTPS enforcement
- No insecure cryptographic practices

**Access control:**
- Public/private/protected scoping correctly applied
- Internal APIs properly marked
- Database access restricted to appropriate users/roles
- File system access properly constrained

**Tools:**
- Security scanners (SonarQube, Bandit for Python)
- Manual code review for auth/secrets patterns
- Dependency vulnerability scanning

**Output:** List of security concerns and required fixes.

### Step 5: Audit API contracts

For APIs (REST, GraphQL, RPC), verify contracts are properly defined and won't break clients.

**Check:**
- Request/response schemas match specification
- Error responses are consistent and documented
- Deprecations are marked and have migration path
- Rate limiting is documented
- Authentication/authorization is documented
- Response time expectations are reasonable
- Pagination is consistent across endpoints
- Versioning strategy is clear

**Tools:**
- OpenAPI/GraphQL schema validation
- Contract testing frameworks
- API documentation generators

**Output:** List of API contract violations.

### Step 6: Check documentation

Verify code is properly documented for maintainability.

**Documentation to check:**
- Docstrings/JSDoc on public functions explain PURPOSE not what
- README/setup instructions are clear
- Complex algorithms have explaining comments
- Non-obvious decisions are flagged ("why", not "what")
- API endpoints documented with examples
- Database schema documented
- Configuration options explained

**Tools:**
- Documentation generators (Sphinx, TypeDoc)
- Comment linting

**Output:** List of missing or poor documentation.

### Step 7: Performance and scalability review

Check for performance issues and potential scalability problems.

**Check for:**
- N+1 query problems (test with realistic data)
- Missing database indexes
- Unnecessary full table scans
- Inefficient algorithms (O(n²) where O(n log n) available)
- Memory leaks or unbounded growth
- Caching where appropriate
- Connection pooling for databases
- Batch operations instead of loops

**Tools:**
- Load testing (k6, JMeter)
- Profiling tools (py-spy, Chrome DevTools)
- Database query analysis (EXPLAIN PLAN)

**Output:** Performance concerns and optimization suggestions.

### Step 8: Compliance validation

Check for compliance with standards (SOC 2, GDPR, PCI-DSS, HIPAA if applicable).

**Check:**
- Data retention policies enforced
- Audit logging present for sensitive operations
- PII data properly encrypted
- Access logging and accountability
- Dependency licenses compliant
- Code version control and history maintained
- Secrets rotation policies followed

**Output:** List of compliance gaps.

### Step 9: Approve or request changes

Summarize findings and approve or request specific changes before merge.

**Approval criteria:**
- All MUST FIX convention violations addressed
- Test coverage meets targets
- Error handling follows patterns
- No security vulnerabilities
- API contracts valid
- Documentation adequate
- Performance acceptable
- Compliance requirements met

**If requesting changes:**
- Be specific: "Line 42: This error should include the user ID for debugging"
- Prioritize: Mark MUST FIX vs NICE TO HAVE
- Explain reasoning: Help developer understand the "why"
- Suggest solutions when non-obvious

**If approving:**
- Confirm all feedback has been addressed
- Check off each category on checklist
- Approve for merge

**Output:** Approval or detailed list of required changes.

### Step 10: Document review findings

Record the review in session file for accountability and learning.

**Session format:**
```
### {timestamp} - review mode
- **Code review:** {files reviewed}
- **Findings:** 
  - MUST FIX: {count} issues
  - NIT: {count} issues
- **Status:** {Approved | Changes requested}
- **Coverage:** {new coverage %}
```

**Output:** Documented review findings in session.
