---
type: subagent
agent: ask
name: docs
variant: verbose
version: 1.0.0
description: Generate and improve documentation with detailed examples
mode: subagent
tools: [write]
workflows:
  - docs-workflow
---

# Documentation (Verbose)

Comprehensive guide for generating inline comments, API documentation, OpenAPI specs, and changelogs.

---

## Inline Comments

### Principles

**Comment the WHY, not the WHAT:**

❌ **Bad (restates code):**
```python
# Increment counter by 1
counter += 1
```

✅ **Good (explains why):**
```python
# Increment before check to avoid off-by-one error in pagination
counter += 1
```

**Skip self-evident code:**

❌ **Unnecessary:**
```python
# Get user by ID
user = get_user_by_id(user_id)
```

✅ **Code is clear enough without comment.**

**Flag non-obvious decisions:**

✅ **Good:**
```python
# Intentionally not awaited — fire and forget for analytics
asyncio.create_task(track_event(user_id, "login"))
```

**Mark known issues:**

✅ **Good:**
```python
# TODO: This will break if called concurrently. Add locking.
def update_counter():
    self.count = self.count + 1
```

**Explain magic numbers:**

❌ **Bad:**
```python
if age > 21:
    ...
```

✅ **Good:**
```python
# 21 = legal drinking age in US
if age > 21:
    serve_alcohol()
```

**Note invariants callers must maintain:**

✅ **Good:**
```python
def process_batch(items):
    """
    Process items in batch.
    
    INVARIANT: items must be sorted by timestamp ascending.
    Caller is responsible for sorting before calling.
    """
    ...
```

### Comment Audit

**Classify existing comments:**

1. **GOOD: Explains something non-obvious → Keep**
   ```python
   # Use binary search because list is pre-sorted by timestamp
   index = bisect.bisect_left(timestamps, target)
   ```

2. **NOISE: Restates what code says → Delete**
   ```python
   # Loop through users
   for user in users:
       ...
   ```

3. **OUTDATED: No longer matches code → Update**
   ```python
   # Returns list of active users
   def get_users():
       return User.query.all()  # ❌ Returns ALL users, not just active
   ```
   Fix to:
   ```python
   # Returns all users (active and inactive)
   def get_users():
       return User.query.all()
   ```

4. **MISSING: Complex code with no explanation → Add**
   ```python
   # ❌ Missing comment on complex logic
   result = (x & 0xFF) << 8 | (y & 0xFF)
   ```
   Fix to:
   ```python
   # Pack x and y bytes into 16-bit integer (x in high byte, y in low byte)
   result = (x & 0xFF) << 8 | (y & 0xFF)
   ```

---

## Function/API Documentation

### Required Elements

For each function, document:

1. **Purpose** — What it does (not how), one sentence
2. **Parameters** — Name, type, required/optional, constraints
3. **Return value** — Type, shape, possible values
4. **Errors** — What fails and under what conditions
5. **Example** — Realistic usage
6. **Side effects** — DB writes, external calls, state changes

### Python Example (Google-style docstring)

```python
def create_user(email: str, password: str, role: str = "user") -> User:
    """
    Create a new user account with email and password.
    
    Args:
        email: User's email address. Must be valid format and unique.
        password: Plain-text password. Must be at least 12 characters.
        role: User role. Must be one of: "user", "admin", "moderator".
              Defaults to "user".
    
    Returns:
        User: The created user object with ID, email, and hashed password.
    
    Raises:
        ValueError: If email format is invalid or password is too short.
        DuplicateEmailError: If email already exists in database.
        DatabaseError: If database write fails.
    
    Side Effects:
        - Writes new user record to database
        - Sends welcome email via SendGrid
        - Logs user creation event to audit log
    
    Example:
        >>> user = create_user("alice@example.com", "SecurePass123!", role="admin")
        >>> print(user.id)
        42
        >>> print(user.email)
        alice@example.com
    
    Note:
        Password is hashed using bcrypt before storage. Plain-text password
        is never stored in database.
    """
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    
    if not is_valid_email(email):
        raise ValueError(f"Invalid email format: {email}")
    
    if User.query.filter_by(email=email).first():
        raise DuplicateEmailError(f"Email already exists: {email}")
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = User(email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    
    send_welcome_email(user.email)
    log_audit_event("user_created", user_id=user.id)
    
    return user
```

### TypeScript Example (JSDoc)

```typescript
/**
 * Fetch user profile with optional related data.
 * 
 * @param userId - Unique user identifier (UUID)
 * @param options - Optional configuration
 * @param options.includeOrders - Include user's order history
 * @param options.includePosts - Include user's posts
 * @returns Promise resolving to User object or null if not found
 * @throws {ValidationError} If userId is not a valid UUID
 * @throws {DatabaseError} If database query fails
 * 
 * @example
 * ```typescript
 * const user = await fetchUser("123e4567-e89b-12d3-a456-426614174000", {
 *   includeOrders: true
 * });
 * 
 * if (user) {
 *   console.log(user.email);
 *   console.log(user.orders?.length);
 * }
 * ```
 * 
 * @remarks
 * This function performs a database query. Use caching for frequently
 * accessed users to reduce database load.
 */
async function fetchUser(
  userId: string,
  options?: { includeOrders?: boolean; includePosts?: boolean }
): Promise<User | null> {
  if (!isValidUUID(userId)) {
    throw new ValidationError("userId must be a valid UUID");
  }
  
  const query = db.users.where({ id: userId });
  
  if (options?.includeOrders) {
    query.include("orders");
  }
  
  if (options?.includePosts) {
    query.include("posts");
  }
  
  return await query.first();
}
```

---

## OpenAPI Spec

### Template (OpenAPI 3.0 YAML)

```yaml
openapi: 3.0.3
info:
  title: User Management API
  version: 1.0.0
  description: API for managing user accounts and authentication

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List all users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: Number of users per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Successfully retrieved user list
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer
                    description: Total number of users
                  page:
                    type: integer
                  limit:
                    type: integer
        '400':
          description: Invalid query parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized - missing or invalid token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []

    post:
      summary: Create new user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                  example: alice@example.com
                password:
                  type: string
                  minLength: 12
                  example: SecurePass123!
                role:
                  type: string
                  enum: [user, admin, moderator]
                  default: user
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input (e.g., weak password, invalid email)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Conflict - email already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []

  /users/{userId}:
    get:
      summary: Get user by ID
      operationId: getUserById
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          description: User ID (UUID)
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - role
        - createdAt
      properties:
        id:
          type: string
          format: uuid
          example: 123e4567-e89b-12d3-a456-426614174000
        email:
          type: string
          format: email
          example: alice@example.com
        role:
          type: string
          enum: [user, admin, moderator]
        createdAt:
          type: string
          format: date-time
          example: 2026-04-10T14:30:00Z
        updatedAt:
          type: string
          format: date-time
          example: 2026-04-10T14:30:00Z

    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          example: VALIDATION_ERROR
        message:
          type: string
          example: Email format is invalid

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Changelog

### Format: Keep a Changelog

**Sections (in order):**
- **Added** — New features
- **Changed** — Changes to existing functionality
- **Deprecated** — Soon-to-be-removed features
- **Removed** — Removed features
- **Fixed** — Bug fixes
- **Security** — Security vulnerability fixes

### Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Webhook support for event streaming (#234)
- Rate limiting for /login endpoint (100 requests/min) (#245)

### Changed
- User session timeout reduced from 60 minutes to 30 minutes (#240)

## [2.1.0] - 2026-04-10

### Added
- User profile image upload via /users/{id}/avatar endpoint (#220)
- Email verification for new accounts (#225)
- Two-factor authentication (TOTP) support (#230)

### Changed
- Password minimum length increased from 8 to 12 characters (#221)
- API response times improved by 40% via query optimization (#228)

### Fixed
- JWT token refresh fails after 7 days (expired refresh token) (#223)
- User deletion doesn't cascade to related orders (#226)

### Security
- Fixed XSS vulnerability in user bio field (CVE-2026-12345) (#229)

## [2.0.0] - 2026-03-15

### Added
- Complete REST API for user management
- JWT-based authentication
- Role-based access control (user, admin, moderator)

### Changed
- ⚠️ BREAKING: API base path changed from /api to /api/v1
- ⚠️ BREAKING: Authentication now requires JWT tokens (was cookie-based)

### Removed
- ⚠️ BREAKING: Removed /auth/session endpoint (replaced by /auth/token)

### Deprecated
- /users/search endpoint (use /users?query=... instead, removal in v3.0)

[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/releases/tag/v2.0.0
```

### Changelog Guidelines

**✅ Write for consumers (not implementers):**

❌ **Bad (implementation detail):**
```
- Refactored authentication module to use dependency injection
```

✅ **Good (user impact):**
```
- Improved authentication reliability (fewer intermittent login failures)
```

**Include internal changes only if user-facing:**

❌ **Exclude:**
```
- Switched from pytest to unittest  # Doesn't affect users
```

✅ **Include:**
```
- Test coverage increased from 70% to 90%  # Implies higher quality
```

**Prefix breaking changes:**

✅ **Correct:**
```
### Changed
- ⚠️ BREAKING: API now requires authentication for /users endpoint
```

**Ask for missing info:**

If version or date not provided:
- "What version should this be? (e.g., 2.1.0)"
- "What release date? (YYYY-MM-DD)"
