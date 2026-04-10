---
name: code-feature-verbose
version: 1.0.0
description: Detailed feature implementation guide with examples
tags: [code, feature, verbose]
tools: [read]
---

# Code Feature (Verbose)

Complete guide to implementing features from requirements to delivery.

## Philosophy

Feature implementation is a deliberate process: understand before building, confirm before committing, test before shipping. Rushing to code without understanding leads to rework.

## Complete Implementation Workflow

### Phase 1: Understanding (Pre-Implementation)

#### Step 1.1: Restate the Goal

Before writing any code, restate what you understand:

**User request:**
> "Add rate limiting to the /auth endpoint"

**Your restatement:**
> "I understand you want to add rate limiting to prevent brute force attacks on the authentication endpoint. The rate limit should block requests from the same IP address after N failed attempts within a time window. Is this correct?"

**Why this matters:**
- Catches misunderstandings early
- Clarifies ambiguous requirements
- Establishes shared understanding

#### Step 1.2: Read Relevant Source Files

Never assume file contents. Read before modifying:

```bash
# Identify files to read
grep -r "def login" src/
grep -r "@app.route.*auth" src/

# Read the files
cat src/routes/auth.py
cat src/middleware/rate_limiter.py  # if exists
```

**What to look for:**
- Current implementation structure
- Existing error handling patterns
- How similar features are implemented
- Configuration management approach

#### Step 1.3: Identify All Files to Change

List every file that needs modification:

**Example:**
```
Files to modify:
1. src/routes/auth.py - Add rate limiting decorator
2. src/middleware/rate_limiter.py - Create if doesn't exist
3. src/config/settings.py - Add rate limit configuration
4. tests/test_auth.py - Add rate limiting tests
5. .env.example - Document new config vars
```

#### Step 1.4: Propose Implementation Approach

Present your plan with tradeoffs:

**Example:**
```
Implementation Approach:

Option A: In-memory rate limiting (chosen)
- Store request counts in Redis with TTL
- Pros: Fast, distributed-safe, automatic cleanup
- Cons: Requires Redis dependency
- Risk: Redis downtime = no rate limiting

Option B: Database-based rate limiting
- Store request counts in PostgreSQL
- Pros: No new dependency, persistent records
- Cons: Slower, requires cleanup job

Recommendation: Option A (Redis)
Rationale: Speed is critical for auth endpoint

Assumptions:
- Redis is available in all environments
- Rate limit is 5 requests per 15 minutes
- Block duration is 15 minutes after limit hit

Please confirm this approach before I proceed.
```

#### Step 1.5: Flag Assumptions

Explicitly state what you're assuming:

**Example:**
```
Assumptions I'm making:
1. Rate limit applies to failed login attempts only
2. IP address is reliable identifier (not behind proxy)
3. Existing logging will capture rate limit events
4. No differentiation between user types

Please correct any wrong assumptions.
```

### Phase 2: Implementation

#### Step 2.1: Follow Core Conventions

Match patterns from existing codebase:

**Example: Error Handling Pattern**

Existing pattern in codebase:
```python
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id: str) -> Response:
    try:
        user = user_service.get_user(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

Your implementation should match this pattern.

#### Step 2.2: Add Inline Comments for Non-Obvious Logic

**Good comments:**
```python
# Fail open - don't block legitimate users if Redis is unavailable
if redis_client is None:
    return (False, 0)

# Use INCR + EXPIRE instead of GET + SET to avoid race conditions
count = redis_client.incr(key)
if count == 1:
    redis_client.expire(key, RATE_LIMIT_WINDOW)
```

**Bad comments (don't do this):**
```python
# Increment the counter
count = redis_client.incr(key)

# Check if count is greater than max
if count > MAX_REQUESTS:
    return True
```

#### Step 2.3: Add TODO for Judgment Calls

Mark decisions the user should review:

```python
def check_rate_limit(ip: str) -> tuple[bool, int]:
    # TODO: Should we rate limit by IP or by user_id?
    # Currently using IP, but this won't work behind proxies
    # Consider using X-Forwarded-For header
    key = f"rate_limit:{ip}"
    
    # TODO: Should failed Redis calls fail open or fail closed?
    # Currently failing open (allowing requests)
    try:
        count = redis_client.incr(key)
    except RedisError:
        return (False, 0)  # Fail open
```

#### Step 2.4: Work Incrementally

Implement one file at a time:

1. **First: Core logic (rate limiter)**
2. **Second: Integration (apply to endpoint)**
3. **Third: Configuration**
4. **Fourth: Tests**

### Phase 3: Post-Implementation

#### Step 3.1: List Follow-Up Work

**Example:**
```markdown
## Follow-Up Work Created

### Tech Debt
1. Rate limiter fails open if Redis is down - should we fail closed?
2. No metrics/alerting for rate limit hits
3. Rate limit is global - should differentiate by user type

### Missing Tests
1. Integration test: verify rate limit blocks after N attempts
2. Integration test: verify rate limit resets after time window
3. Unit test: verify fail-open behavior when Redis errors

### Related Changes Needed
1. Update API documentation with rate limit details
2. Add rate limit headers to all responses
3. Consider adding rate limiting to other endpoints
```

#### Step 3.2: Document Testing Needs

**Example:**
```markdown
## Tests to Write

### Unit Tests (src/middleware/rate_limiter.py)
1. test_check_rate_limit_allows_under_limit
   - Given: IP with 3 requests in window (limit is 5)
   - When: check_rate_limit() called
   - Then: returns (False, 0)

2. test_check_rate_limit_blocks_over_limit
   - Given: IP with 6 requests in window (limit is 5)
   - When: check_rate_limit() called
   - Then: returns (True, retry_after_seconds)

### Integration Tests (tests/test_auth.py)
1. test_login_rate_limit_blocks_after_max_attempts
   - Given: No prior requests from IP
   - When: 6 failed login attempts from same IP
   - Then: 6th attempt returns 429 with Retry-After header

### Edge Cases to Cover
1. Successful login doesn't count toward rate limit
2. Different IPs have independent rate limits
3. Rate limit survives application restart
```

## Complete Example: Add User Export Feature

### User Request
> "Add ability to export user data to CSV"

### Step 1: Restate Understanding

**Response:**
> I understand you want to add a CSV export feature for user data. I assume this means:
> - Export all users in the database
> - Include fields: id, email, name, created_at, status
> - Available to admin users only
> - Accessed via new /admin/users/export endpoint
> 
> Is this correct? Are there any specific fields to include/exclude?

### Step 2: Read Source Files

```bash
# Find existing admin routes
grep -r "@admin" src/routes/

# Find user model
find src -name "*user*model*"

# Read files
cat src/routes/admin.py
cat src/models/user.py
```

### Step 3: Propose Approach

**Response:**
```markdown
## Implementation Plan

### Files to Modify
1. src/routes/admin.py - Add /admin/users/export endpoint
2. src/services/export_service.py - Create new service
3. tests/test_admin_routes.py - Add export tests

### Approach

Option A: In-memory CSV generation (chosen)
- Query all users from database
- Build CSV in memory using Python csv module
- Stream response to client
- Pros: Simple, works for small datasets
- Cons: Memory issues if 100k+ users

Recommendation: Start with Option A (in-memory)
Rationale: Current user count is ~5k, in-memory is sufficient

### Assumptions
- Export includes ALL users (no filtering/pagination)
- CSV fields: id, email, name, created_at, status, role
- Only admin users can access
- Export is synchronous

Please confirm this approach.
```

### Step 4: Implementation

**File 1: src/services/export_service.py**
```python
import csv
from io import StringIO
from src.models.user import User

class ExportService:
    """Service for exporting data to various formats."""
    
    def generate_user_csv(self, users: list[User]) -> str:
        """Generate CSV string from user list."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Email', 'Name', 'Created At', 'Status', 'Role'])
        
        # Write user data
        for user in users:
            writer.writerow([
                user.id,
                user.email,
                user.name,
                user.created_at.isoformat(),
                user.status,
                user.role,
            ])
        
        return output.getvalue()
```

**File 2: src/routes/admin.py**
```python
from flask import Response
from src.services.export_service import ExportService
import datetime

@app.route('/admin/users/export', methods=['GET'])
@admin_required
def export_users() -> Response:
    """Export all users to CSV file."""
    users = UserService.get_all_users()
    export_service = ExportService()
    csv_data = export_service.generate_user_csv(users)
    
    filename = f"users_export_{datetime.date.today().isoformat()}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
```

### Step 5: Follow-Up

**Response:**
```markdown
## Implementation Complete

### Files Modified
1. src/services/export_service.py - Created (52 LOC)
2. src/routes/admin.py - Added export endpoint (15 LOC)
3. tests/test_export_service.py - Created (28 LOC)

### Follow-Up Work

#### Tech Debt
1. In-memory CSV generation won't scale beyond ~50k users
2. No progress indicator for large exports
3. No audit logging for who exported data

#### Missing Tests
1. Integration test: verify CSV download with proper headers
2. Security test: verify non-admin cannot access endpoint
3. Edge case: empty user list generates header-only CSV

#### Related Changes
1. Update admin documentation with export feature
2. Consider adding date range filter for exports
```

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Implementing Before Understanding

**Wrong:** User asks to add rate limiting, you immediately start writing code.

**Correct:** Restate understanding, ask clarifying questions, propose approach, wait for confirmation.

### ❌ Anti-Pattern 2: Assuming File Contents

**Wrong:** Assuming auth.py has a login function without reading it.

**Correct:** Read the file first, understand actual structure, then implement.

### ❌ Anti-Pattern 3: Silent Scope Creep

**Wrong:** User asks to add CSV export, you also refactor the user service, optimize database queries, and add caching.

**Correct:** Implement only CSV export. If you see opportunities for improvement, mention them but don't implement without asking.

## Workflow Checklist

```markdown
### Pre-Implementation
- [ ] Restated goal in own words
- [ ] Asked clarifying questions
- [ ] Read all relevant source files
- [ ] Identified all files to modify
- [ ] Proposed implementation approach with tradeoffs
- [ ] Flagged all assumptions
- [ ] Received user confirmation

### Implementation
- [ ] Following Core Conventions
- [ ] Matching patterns from existing code
- [ ] Added inline comments for non-obvious logic
- [ ] Added TODO for judgment calls
- [ ] Working one file at a time
- [ ] Testing incrementally

### Post-Implementation
- [ ] Listed tech debt created
- [ ] Listed missing tests
- [ ] Listed related changes needed
- [ ] Documented testing strategy
- [ ] Verified all acceptance criteria met
```
