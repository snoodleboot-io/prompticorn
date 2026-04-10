<!-- path: promptosaurus/.kilocode/rules-document/workflow-verbose.md -->
# Documentation Workflow - Verbose Version

**Metadata:**
- languages: [all]
- subagents: [document/api, document/strategy]
- target_audience: Senior engineers, technical writers, developers
- estimated_time: 4-12 hours
- complexity: high

## 1. Documentation Types & Purposes

### API Reference (How to use what exists)
**Purpose:** Technical reference for developers using your code  
**Audience:** Developers, API consumers  
**Structure:**
- Function/method signature
- Parameter descriptions (types, constraints)
- Return value description
- Exception/error documentation
- Real usage example
- Related functions/methods

**Example Structure:**
```
## createUser(name: string, email: string): Promise<User>

Creates a new user account. The email must be unique and valid.

**Parameters:**
- `name` (string, required): User display name, 1-100 characters
- `email` (string, required): Valid email address, must be unique

**Returns:** Promise<User> - Resolves with newly created user object

**Throws:**
- `ValidationError`: Email invalid or name too short
- `ConflictError`: Email already registered

**Example:**
\`\`\`javascript
const user = await createUser("Alice", "alice@example.com");
// { id: "123", name: "Alice", email: "alice@example.com" }
\`\`\`

**See Also:** updateUser(), deleteUser()
```

### User Guide (How to accomplish tasks)
**Purpose:** Step-by-step instructions for common workflows  
**Audience:** End users, developers implementing workflows  
**Structure:**
- High-level overview (what will you accomplish?)
- Prerequisites (what must be true first?)
- Step-by-step instructions
- Expected output/verification
- Common mistakes and how to avoid them
- Link to reference documentation for details

**Example Structure:**
```
## How to Implement User Authentication

After completing this guide, users will be able to log in with email and password.

**Prerequisites:**
- Node.js 18+ installed
- Database connection established
- createUser() endpoint working

**Steps:**

1. **Create login form**
   - Username/email field
   - Password field
   - Submit button

2. **Call login endpoint**
   \`\`\`javascript
   const response = await fetch('/api/login', {
     method: 'POST',
     body: JSON.stringify({ email, password })
   });
   \`\`\`

3. **Store session token**
   - Save token to localStorage
   - Include in Authorization header for future requests

4. **Handle errors**
   - Check response status
   - Display error message to user
   - Don't store invalid tokens

**Expected Result:**
User is logged in, can access protected endpoints

**Common Mistakes:**
- Storing plaintext password (use hash!)
- Not validating email format
- Token expiration not handled

**See Also:** API Reference → /api/login, Security Guide → Password Hashing
```

### Examples & Code Samples (How it works in practice)
**Purpose:** Realistic, working code showing common patterns  
**Audience:** Developers learning the system  
**Requirements:**
- MUST actually run without modification
- Should demonstrate one concept per example
- Include both success and error cases
- Explain what the example shows

**Example Structure:**
```
## Example: Paginated User List

This example shows how to fetch users with pagination.

\`\`\`python
from api_client import Client

client = Client(api_key="YOUR_KEY")

# Fetch first page (default 20 items)
response = client.users.list(page=1)

for user in response.data:
    print(f"{user.name}: {user.email}")

# Fetch next page
if response.has_next:
    next_response = client.users.list(page=2)
\`\`\`

**What this example shows:**
- How to create a client
- How to list users with default pagination
- How to check if more pages exist
- How to fetch the next page

**Output:**
\`\`\`
Alice: alice@example.com
Bob: bob@example.com
Charlie: charlie@example.com
...
\`\`\`

**See Also:** API Reference → list(), Pagination Guide
```

### Troubleshooting & FAQ (What went wrong and how to fix it)
**Purpose:** Help users solve common problems independently  
**Audience:** Users experiencing issues  
**Structure:**
- Error message or symptom
- Root causes (what usually causes this?)
- Diagnostic steps (how to verify which cause)
- Solution for each cause
- Prevention tips

**Example Structure:**
```
## Troubleshooting: Authentication Failures

**Symptom:** "401 Unauthorized" error when calling API

**Root Causes:**
1. Token expired (most common, ~70% of cases)
2. Wrong API key (misconfiguration, ~20%)
3. Permission insufficient (insufficient scopes, ~10%)

**Diagnostic Steps:**

1. Check token expiration:
   \`\`\`bash
   curl -H "Authorization: Bearer $TOKEN" https://api.example.com/auth/verify
   \`\`\`
   - If error: token is invalid/expired
   - If success: token is valid

2. Check API key format:
   \`\`\`
   - Length: Should be 32+ characters
   - Format: Should be alphanumeric or base64
   - Location: Should be in Authorization header
   \`\`\`

3. Check permissions:
   \`\`\`bash
   curl -H "Authorization: Bearer $TOKEN" https://api.example.com/auth/scopes
   \`\`\`
   - Compare required vs granted scopes

**Solutions:**

**If token expired:**
- Call refresh endpoint to get new token
- Store new token in env variable
- Update your code to handle token refresh

**If API key wrong:**
- Verify key matches what's shown in dashboard
- Check key hasn't been rotated
- Create new key if unsure

**If permissions insufficient:**
- Log into dashboard
- Add required scopes to API key
- Wait 30 seconds for propagation
- Try request again

**Prevention:**
- Set token refresh 5 minutes before expiry
- Store API keys in environment variables, never hardcoded
- Test with minimal required scopes first
```

### Architecture & Design Documentation (How pieces fit together)
**Purpose:** Help developers understand system design  
**Audience:** New contributors, architects  
**Structure:**
- Conceptual diagram (boxes and arrows)
- Description of each component
- Data flows between components
- Key design decisions and tradeoffs
- Link to decision log (ADR) for details

**Example Structure:**
```
## Architecture Overview

\`\`\`
┌─────────────┐
│   Browser   │  (User's client)
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────┐
│   API Server    │  (Express.js)
├─────────────────┤
│ Auth Middleware │
│ Request Router  │
└────────┬────────┘
         │ SQL
         ▼
┌─────────────────┐
│    Database     │  (PostgreSQL)
├─────────────────┤
│ Users, Sessions │
│ API Keys, Logs  │
└─────────────────┘
\`\`\`

**Components:**

**Browser:** User-facing frontend
- Makes HTTP requests to API
- Stores session tokens in localStorage
- Never stores sensitive data

**API Server:** Request handler and business logic
- Authenticates requests via middleware
- Routes to handlers
- Returns JSON responses
- Logs all requests

**Database:** Persistent data storage
- Stores user accounts and sessions
- Indexes on frequently-queried columns
- Backup taken daily

**Data Flows:**

1. **Login Flow:**
   Browser → POST /auth/login → API (validate) → DB (check user) → API (generate token) → Browser

2. **API Call Flow:**
   Browser → GET /api/users (+ token) → API (verify token) → DB (fetch users) → API (return JSON) → Browser

**Key Design Decisions:**
- Stateless API (no session stickiness required)
- JWT tokens for authentication (allows scaling)
- Single database (no sharding yet)

**See Also:** ADR-003 Authentication Strategy, ADR-004 Stateless API Design
```

## 2. Pre-Documentation Analysis

### Step 2.1: Understand the Code First
Before writing ANY documentation:
```
CODE ANALYSIS CHECKLIST:
- [ ] Read all public exports/APIs
- [ ] Run the code locally to understand behavior
- [ ] Identify edge cases and error conditions
- [ ] Check for existing documentation (READMEs, comments, examples)
- [ ] Understand dependencies and constraints
- [ ] Identify what would confuse a new developer
```

### Step 2.2: Identify Documentation Gaps
Determine what documentation exists and what's missing:
```
DOCUMENTATION INVENTORY:
- [ ] README exists and current? Y/N
- [ ] API reference exists? Y/N
- [ ] Usage examples exist? Y/N
- [ ] Troubleshooting guide exists? Y/N
- [ ] Architecture docs exist? Y/N
- [ ] Setup/installation guide? Y/N
- [ ] Contributing guide? Y/N
- [ ] Decision log (ADRs) exists? Y/N

GAPS TO FILL (pick which to document):
- [ ] High-level overview
- [ ] Getting started guide
- [ ] API reference details
- [ ] Error handling guide
- [ ] Performance notes
- [ ] Security best practices
- [ ] Version compatibility
```

### Step 2.3: Audience Identification
Determine who will read each piece of documentation:
```
DOCUMENTATION AUDIENCE:

For this documentation, target:
- [ ] Internal developers (building the system)
- [ ] API consumers (using the system)
- [ ] DevOps/SRE (deploying the system)
- [ ] New contributors (learning the system)
- [ ] End users (using features)

Adjust:
- Terminology (jargon level)
- Code examples (language, complexity)
- Detail level (deep technical vs high-level)
- Format (API reference vs tutorial)
```

## 3. Inline Comments & Code Documentation

### 3.1: Inline Comment Strategy

**Rule: Comment the WHY, not the WHAT**

✗ **Bad (restates code):**
```python
# Increment counter
counter = counter + 1

# Check if email is valid
if "@" in email:
    process(email)
```

✓ **Good (explains intent):**
```python
# Increment retry count — will abort if exceeds 3
counter = counter + 1

# Filter out invalid email formats before API call
# (upstream API will reject, better to fail fast here)
if "@" in email:
    process(email)
```

### 3.2: Comment Classification Audit
When reviewing existing comments, classify as:

**GOOD Comments (Keep):**
- Explain non-obvious decisions
- Document invariants (what must always be true)
- Note gotchas or edge cases
- Mark known issues or TODOs with context
- Explain magic numbers or constants

**NOISE Comments (Delete):**
- Restate what the code clearly shows
- Comment on obvious operations
- Describe variable names that are self-documenting
- Outdated comments describing old behavior

**OUTDATED Comments (Update):**
- Don't match current code behavior
- Reference removed/renamed variables
- Point to wrong file/function names
- Document removed features

**MISSING Comments (Add):**
- Complex logic with no explanation
- Non-obvious performance choices
- Explain why pattern X was chosen over Y
- Document thread-safety or concurrency assumptions

### 3.3: Comment Standards
Establish patterns for consistency:

```python
# Pattern 1: Magic number explanation
SECONDS_PER_DAY = 86400  # 60 * 60 * 24

# Pattern 2: Gotcha warning
# NOTE: This will raise an error if called twice on same object
# (state is modified in-place, not idempotent)
def process(data):
    data['processed'] = True
    return data

# Pattern 3: Intentional design choice
# Intentionally not awaited — fire and forget
# (caller doesn't need confirmation, reduces latency)
sendAnalytics(event)

# Pattern 4: Workaround explanation
# TODO: Use proper async/await when Python 3.5+ available
# Current workaround creates new thread as callback
threading.Thread(target=async_task).start()

# Pattern 5: Concurrency warning
# WARNING: Race condition if called concurrently
# (not yet thread-safe, caller must serialize access)
def update_shared_state(value):
    shared['value'] = value
```

## 4. Function & API Documentation

### 4.1: Docstring Template

**For Python (Google style):**
```python
def create_user(name: str, email: str) -> User:
    """Create a new user account.
    
    Creates a new user with the provided name and email. Email must be
    unique and valid. Returns immediately; no confirmation sent.
    
    Args:
        name: User display name, 1-100 characters.
        email: Valid email address. Must be unique in system.
    
    Returns:
        User object with id, name, email, created_at fields.
    
    Raises:
        ValidationError: If name too short/long or email invalid.
        ConflictError: If email already registered in system.
    
    Examples:
        >>> user = create_user("Alice", "alice@example.com")
        >>> user.name
        'Alice'
    """
```

**For JavaScript (JSDoc):**
```javascript
/**
 * Create a new user account.
 * 
 * Creates a new user with the provided name and email. Email must be
 * unique and valid. Returns immediately; no confirmation sent.
 * 
 * @param {string} name - User display name, 1-100 characters.
 * @param {string} email - Valid email address, must be unique.
 * @returns {Promise<User>} User object with id, name, email, created_at.
 * @throws {ValidationError} If name too short/long or email invalid.
 * @throws {ConflictError} If email already registered in system.
 * 
 * @example
 * const user = await createUser("Alice", "alice@example.com");
 * console.log(user.name); // "Alice"
 */
```

### 4.2: Docstring Content Checklist

For each public function/method, document:

```
DOCSTRING CHECKLIST:
- [ ] Purpose statement (one sentence: what it does)
- [ ] Detailed description (what, how, why)
- [ ] Parameters (name, type, required/optional, constraints)
- [ ] Return value (type, shape, meaning of null/undefined)
- [ ] Errors/Exceptions (what can go wrong, when, what to do)
- [ ] Side effects (DB writes, external calls, state changes)
- [ ] Example (realistic usage with realistic inputs/outputs)
- [ ] Performance notes (if relevant — slow operation, N+1 risk, etc.)
- [ ] Thread-safety (if relevant — concurrent access safe?)
- [ ] Related functions (link to similar/related functions)
```

### 4.3: Common Documentation Mistakes

**Mistake 1: Vague parameter descriptions**
```
✗ BAD: "user: user object"
✓ GOOD: "user: User object with at least id and email fields"

✗ BAD: "timeout: timeout value"
✓ GOOD: "timeout: Timeout in milliseconds, 0-30000, default 5000"
```

**Mistake 2: No error documentation**
```
✗ BAD: function throws errors (true but useless)
✓ GOOD: Throws ValidationError if email invalid, ConflictError if exists
```

**Mistake 3: Outdated examples**
```
✗ BAD: Example uses deprecated API
✓ GOOD: Run examples before committing, keep updated
```

**Mistake 4: No side effects documented**
```
✗ BAD: Silent about what happens internally
✓ GOOD: "NOTE: Sends confirmation email, updates cache, logs event"
```

## 5. README Documentation

### 5.1: README Must Answer Four Questions

```
QUESTION 1: What does this do?
(One paragraph, no jargon, clear value)

Answer: "This is a Python library for [specific problem]. 
It lets you [primary benefit] in [time/effort]."

QUESTION 2: How do I run it locally?
(Exact commands, not prose)

Answer:
\`\`\`bash
git clone ...
cd ...
pip install -r requirements.txt
python -m pytest
\`\`\`

QUESTION 3: How do I run the tests?
(Command that runs full test suite)

Answer:
\`\`\`bash
pytest                    # Run all tests
pytest --cov             # With coverage
pytest tests/unit/       # Only unit tests
\`\`\`

QUESTION 4: How is the code organized?
(One sentence per major directory)

Answer:
\`\`\`
src/
  core/        - Business logic and algorithms
  api/         - HTTP endpoints and routing
  db/          - Database models and queries
  util/        - Shared utilities
tests/
  unit/        - Fast, isolated tests
  integration/ - Multi-component tests
docs/          - User guides and architecture docs
\`\`\`
```

### 5.2: Additional README Sections

```
Additional sections (in order of importance):

[ ] Installation
    - Requirements (Node/Python/etc version)
    - Step-by-step install

[ ] Quick Start
    - Minimal example to get running
    - 5-10 lines of code max

[ ] API Reference
    - Link to detailed API docs
    - OR brief summary if small API

[ ] Configuration
    - Environment variables
    - Config file format (if applicable)

[ ] Troubleshooting
    - Common errors
    - How to debug

[ ] Performance Notes
    - Known limitations
    - Scaling considerations

[ ] Contributing
    - How to set up dev environment
    - Testing requirements
    - Code style expectations

[ ] License
    - Which license (MIT, Apache, etc.)

[ ] Decision Log
    - Link to ADRs explaining major decisions
```

### 5.3: README Anti-Patterns (What NOT to do)

**Mistake 1: Marketing copy**
```
✗ BAD: "This revolutionary library will change your life!"
✓ GOOD: "This library provides X functionality, reducing Y by Z%"
```

**Mistake 2: Aspirational features**
```
✗ BAD: "Future features: clustering, ML support, etc."
✓ GOOD: (Remove or move to backlog)
```

**Mistake 3: Broken examples**
```
✗ BAD: Example doesn't run as written
✓ GOOD: Test all examples before committing
```

**Mistake 4: Wrong section in README**
```
✗ BAD: Detailed architecture explanation (belongs in docs/)
✗ BAD: API parameter reference (belongs in docstrings/API docs)
✓ GOOD: Use README for overview, link to details elsewhere
```

## 6. API Documentation (OpenAPI/Swagger)

### 6.1: OpenAPI Structure

```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0

paths:
  /users:
    post:
      summary: Create a new user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name, email]
              properties:
                name:
                  type: string
                  minLength: 1
                  maxLength: 100
                  description: User display name
                email:
                  type: string
                  format: email
                  description: Valid email address
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid request (email invalid, name empty)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Email already registered
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          description: Unique user identifier
        name:
          type: string
        email:
          type: string
        created_at:
          type: string
          format: date-time
    
    Error:
      type: object
      properties:
        code:
          type: string
          enum: [VALIDATION_ERROR, CONFLICT_ERROR]
        message:
          type: string
```

### 6.2: OpenAPI Checklist

```
OPENAPI DOCUMENTATION CHECKLIST:
- [ ] Every endpoint documented
- [ ] Request body schema documented (required fields marked)
- [ ] Response schemas for all status codes (200, 400, 401, 404, 500)
- [ ] Error responses documented (not just 200)
- [ ] Parameter descriptions clear and constraints noted
- [ ] Authentication method documented (API key, JWT, OAuth)
- [ ] Rate limits documented (if applicable)
- [ ] Examples provided for requests/responses
- [ ] Endpoints tagged by resource
- [ ] Version documented
```

## 7. Examples & Code Samples

### 7.1: Example Requirements

Every example MUST:
```
EXAMPLE REQUIREMENTS:
- [ ] Actually runs without modification
- [ ] Demonstrates one clear concept
- [ ] Uses realistic data (not trivial examples)
- [ ] Shows expected output
- [ ] Includes both success and error cases
- [ ] Code is formatted and properly indented
- [ ] Syntax highlighting language specified
```

### 7.2: Example Testing

Before committing examples, test them:

```bash
# Python examples
python < example.py

# JavaScript examples
node example.js

# Shell examples
bash example.sh
```

Automated example testing (CI):
```bash
# Extract and test all code blocks in markdown
pytest --doctest-modules docs/*.md
```

### 7.3: Example Structure

```markdown
## Example: [Clear title describing what this shows]

[1-2 sentences explaining what you'll accomplish]

\`\`\`python
from client import API

client = API()

# Get users from the system
response = client.users.list()

# Print first 5 users
for user in response.data[:5]:
    print(f"{user.name}: {user.email}")
\`\`\`

**Output:**
\`\`\`
Alice: alice@example.com
Bob: bob@example.com
Charlie: charlie@example.com
David: david@example.com
Eve: eve@example.com
\`\`\`

**What this example shows:**
- How to create an API client
- How to list users
- How to iterate over results
- How to access user properties

**Related Examples:** [Link to similar examples]
```

## 8. Troubleshooting & FAQ Documentation

### 8.1: FAQ Template

```markdown
## FAQ: Common Questions

### Q: How do I do X?
A: [Clear, step-by-step answer]

### Q: Why does Y happen?
A: [Explanation of root cause]

### Q: What's the difference between A and B?
A: [Clear comparison]
```

### 8.2: Troubleshooting Template

```markdown
## Troubleshooting: [Error Type]

**Symptom:** [What the user observes]

**Root Causes:**
1. [Cause 1] — [How common] — [Quick test]
2. [Cause 2] — [How common] — [Quick test]
3. [Cause 3] — [How common] — [Quick test]

**How to diagnose:**
\`\`\`bash
[Command to check which cause]
\`\`\`

**Solutions:**

**If Cause 1:** [Steps to fix]
**If Cause 2:** [Steps to fix]
**If Cause 3:** [Steps to fix]

**Still not working?** [How to get help/report issue]
```

## 9. Documenting Decisions (Architecture Decision Records)

### 9.1: ADR Format

```markdown
# ADR-001: Use PostgreSQL Instead of MongoDB

**Date:** 2026-04-10
**Status:** Accepted
**Deciders:** Engineering team

## Context
We're building a new application with relational data requirements.
We need to choose a database.

## Decision
We will use PostgreSQL for primary data storage.

## Alternatives Considered

### MongoDB
- Pros: Flexible schema, horizontal scaling
- Cons: No ACID guarantees, larger storage overhead
- Effort: Medium setup

### MySQL
- Pros: Familiar, solid ACID, good performance
- Cons: Not as advanced for complex queries
- Effort: Low setup

## Consequences

**Positive:**
- ACID compliance ensures data integrity
- Rich query language for complex analytics
- Strong ecosystem and community

**Negative:**
- Requires schema design upfront
- Vertical scaling limits eventually
- Larger memory footprint than some alternatives

**Risks:**
- If we need horizontal scaling later, migration is difficult
- Requires schema migrations (downtime possible)

## Review Date
2027-04-10 (one year)
```

### 9.2: When to Create ADRs

Create an ADR when:
```
ADR DECISION TRIGGERS:
- [ ] Architectural decision (database, messaging, etc.)
- [ ] Major dependency choice (framework, library)
- [ ] Performance optimization that trades complexity for speed
- [ ] Security choice (authentication, encryption approach)
- [ ] Breaking API change with migration path
- [ ] Significant code pattern decision
```

## 10. Verification & Quality Assurance

### 10.1: Documentation Completeness Checklist

```
DOCUMENTATION COMPLETENESS:
- [ ] Overview/README answers: what, how, why
- [ ] API reference: all public functions documented
- [ ] Examples: all key use cases covered, examples tested
- [ ] Troubleshooting: common errors and solutions
- [ ] Architecture: how components fit together
- [ ] Setup: installation and configuration steps
- [ ] Tests: how to run test suite
- [ ] Contributing: how to contribute code
```

### 10.2: Documentation Accuracy Verification

```
ACCURACY VERIFICATION:
- [ ] Read code and verify docs match
- [ ] Run all examples without modification
- [ ] Test all installation steps from scratch
- [ ] Verify all command examples work as written
- [ ] Check all links (internal and external) work
- [ ] Verify API parameter types match documentation
- [ ] Confirm error cases actually produce documented errors
```

### 10.3: Documentation Freshness

```
MAINTENANCE CHECKLIST:
- [ ] Update when code changes
- [ ] Remove outdated examples
- [ ] Update version numbers in docs
- [ ] Verify links still work
- [ ] Review quarterly for accuracy
- [ ] Archive old versions if API changes significantly
```

### 10.4: User Testing

Have someone unfamiliar with the code:
```
USER TESTING:
- [ ] Read overview — is it clear?
- [ ] Follow setup guide — do all steps work?
- [ ] Run examples — do they produce expected output?
- [ ] Find answer to "how do I X?" in docs
- [ ] Find solution to common error in troubleshooting
- [ ] Identify confusing sections

Record feedback and update documentation.
```

## 11. Documentation Tools & Technologies

### Documentation Generators

**API Documentation:**
- Swagger/OpenAPI → SwaggerUI (interactive)
- JavaDoc (Java)
- Sphinx (Python)
- JSDoc (JavaScript)

**Site Generators:**
- MkDocs (Markdown-based, Python)
- Docusaurus (React-based, JavaScript)
- Jekyll (Ruby-based)
- Hugo (Go-based)

**Diagramming:**
- Mermaid (markdown diagrams)
- PlantUML (UML diagrams)
- Diagrams (code-defined diagrams)

### Markdown Best Practices

```markdown
# Heading 1 (File title, use once per file)

## Heading 2 (Section, use for major sections)

### Heading 3 (Subsection, use for details)

**Bold** for emphasis on important terms.
`Inline code` for function names, variables, commands.

\`\`\`python
# Code blocks with language specified
print("Hello")
\`\`\`

- Bullet lists for unordered items
  - Nested items for sub-points

1. Numbered lists for sequences
2. Second step

| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |

[Linked text](https://example.com) for external links
[Internal link](./other-file.md) for docs in same repo

> Blockquotes for important callouts
```

## 12. Complete Documentation Template

```markdown
# [Project Name]

## Overview
[One paragraph: what this is, what problem it solves, who uses it]

## Quick Start
[Minimal example to get running, 5-10 lines max]

## Installation
[Step-by-step install instructions]

## Usage
[Common tasks and how to accomplish them]

### API Reference
[Link to detailed docs or reference section]

### Examples
[Links to multiple example files]

## Configuration
[Environment variables, config files, settings]

## Testing
[How to run test suite]

## Architecture
[How components fit together, link to ADRs]

## Troubleshooting
[Common errors and solutions]

## Contributing
[How to contribute code]

## License
[License type]
```

---

**Total Sections: 12 | Estimated Lines: 200 | Complexity: Comprehensive guide**
