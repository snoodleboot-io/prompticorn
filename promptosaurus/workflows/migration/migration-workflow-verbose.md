---
name: migration-workflow
languages: [all]
subagents: [migration/dependency-upgrade, migration/framework, test/integration]
version: "1.0"
---

# Migration Workflow (Verbose)

## Migration Types

### Framework Upgrades
Migrating between major versions of frameworks (React 17→18, Django 3→4, Spring Boot 2→3).

**Key Concerns:**
- Breaking API changes requiring code rewrites
- Deprecated features that need replacement
- New required configurations
- Performance characteristics changes

### Database Migrations
Schema changes, data type modifications, or database platform switches.

**Key Concerns:**
- Data integrity during migration
- Downtime requirements
- Backward compatibility with running services
- Index rebuilds and performance impact

### Architecture Changes
Monolith to microservices, synchronous to event-driven, REST to GraphQL.

**Key Concerns:**
- Multiple systems changing simultaneously
- Data consistency across service boundaries
- Gradual migration strategy
- Team coordination and deployment sequencing

### Language Version Upgrades
Python 2→3, Java 8→17, Node 14→20, Go 1.18→1.21.

**Key Concerns:**
- Syntax changes and deprecations
- Standard library changes
- Third-party library compatibility
- Performance improvements and regressions

---

## Step 1: Risk Assessment

### High-Risk Migrations
**Indicators:**
- Production database with >1M rows requiring schema changes
- Service with >1000 requests/second requiring zero downtime
- Breaking changes affecting external API consumers
- Migration requiring coordinated deployment of 5+ services

**Mitigation Strategies:**
- Blue-green deployment with traffic switching
- Feature flags to enable/disable new behavior
- Shadow mode where new system runs in parallel without affecting users
- Gradual rollout starting with internal users or low-traffic regions

### Medium-Risk Migrations
**Indicators:**
- Framework upgrade with documented migration path
- Database migration with <100K rows
- Internal API changes affecting known consumers
- Single service deployment

**Mitigation Strategies:**
- Staging environment testing with production-like data
- Automated rollback scripts ready before deployment
- Monitoring dashboards set up to catch regressions
- Communication plan to affected teams

### Low-Risk Migrations
**Indicators:**
- Dependency patch version bump with no breaking changes
- Code refactoring with comprehensive test coverage
- Configuration changes with backward compatibility
- Development tool upgrades (linters, formatters)

**Mitigation Strategies:**
- Standard CI/CD pipeline validation
- Code review with migration checklist
- Staged rollout to canary environment first

---

## Step 2: Plan Migration

### Discovery Phase
**Research Requirements:**
- Read official migration guide from framework/library maintainers
- Search GitHub issues for "migration" to find common problems
- Check Stack Overflow for recent questions about upgrade path
- Review changelog for all intermediate versions between current and target

**Dependency Analysis:**
```bash
# Python - Check dependency compatibility
pip list --outdated
pip-audit  # Security vulnerabilities

# Node.js - Check dependency compatibility
npm outdated
npm audit

# Go - Check for deprecated packages
go list -u -m all
```

**Create Migration Document:**
```markdown
# Migration Plan: React 17 → React 18

## Scope
- 47 components affected by new rendering behavior
- 12 third-party libraries requiring updates
- 3 breaking changes requiring code modifications

## Timeline
- Week 1: Update dependencies, fix breaking changes
- Week 2: Test in staging, performance benchmarks
- Week 3: Gradual production rollout

## Rollback Plan
If error rate increases >2% or p95 latency increases >20%:
1. Revert deployment: `git revert <commit> && git push`
2. Redeploy previous version: `./deploy.sh v2.4.5`
3. Verify metrics return to baseline within 10 minutes
```

### Breaking Changes Audit
**Checklist:**
- [ ] List all deprecated APIs you're currently using
- [ ] Find replacement APIs in new version documentation
- [ ] Estimate code changes required (lines affected, files modified)
- [ ] Identify any runtime behavior changes (async to sync, error handling)
- [ ] Check for configuration file format changes

**Example: Python 2 → 3 Breaking Changes**
```python
# Python 2 code
print "Hello"  # ❌ Syntax error in Python 3
dict.iteritems()  # ❌ Removed in Python 3
unicode()  # ❌ Removed in Python 3

# Python 3 equivalent
print("Hello")  # ✓ Required parentheses
dict.items()  # ✓ Returns iterator by default
str()  # ✓ All strings are unicode
```

---

## Step 3: Data Migration Strategies

### ETL (Extract, Transform, Load)
**When to Use:**
- Switching database platforms (MongoDB → PostgreSQL)
- Major schema redesign
- One-time data transformation
- Acceptable downtime window available

**Implementation:**
```python
# Example: Migrate users from old schema to new schema
import psycopg2

old_conn = psycopg2.connect("postgresql://old_db")
new_conn = psycopg2.connect("postgresql://new_db")

old_cursor = old_conn.cursor()
new_cursor = new_conn.cursor()

# Extract
old_cursor.execute("SELECT id, name, email FROM users")

# Transform and Load
for user_id, name, email in old_cursor:
    # Transform: split name into first_name, last_name
    parts = name.split(' ', 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''
    
    # Load into new schema
    new_cursor.execute(
        "INSERT INTO users (id, first_name, last_name, email) VALUES (%s, %s, %s, %s)",
        (user_id, first_name, last_name, email)
    )

new_conn.commit()
```

### Dual-Write Pattern
**When to Use:**
- Zero-downtime requirement
- Gradual migration over days/weeks
- Need to validate new system before switching reads

**Implementation:**
```python
def save_user(user_data):
    # Write to old system (authoritative during migration)
    old_db.users.insert(user_data)
    
    try:
        # Also write to new system
        new_db.users.insert(transform_user(user_data))
    except Exception as e:
        # Don't fail request if new system has issues
        logger.error(f"Dual-write failed: {e}")
    
    return user_data

# After validation, switch reads to new system
# Then stop writing to old system
```

### Gradual Migration
**When to Use:**
- Large dataset (>1M records)
- Want to migrate small batches to limit risk
- Can tolerate temporary inconsistency

**Implementation:**
```python
# Migrate 1000 users per hour
def migrate_batch():
    users = old_db.users.find({"migrated": False}).limit(1000)
    
    for user in users:
        new_user = transform_user(user)
        new_db.users.insert(new_user)
        old_db.users.update({"_id": user["_id"]}, {"$set": {"migrated": True}})
    
    logger.info(f"Migrated {len(users)} users")

# Schedule with cron: 0 * * * * python migrate_batch.py
```

---

## Step 4: Backward Compatibility

### API Versioning
**Strategy:** Support both old and new API versions during transition period.

```python
# Old API (v1) - deprecated but still supported
@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    users = db.users.find()
    # Old format: flat structure
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

# New API (v2) - current version
@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    users = db.users.find()
    # New format: nested structure with metadata
    return jsonify({
        "users": [{"id": u.id, "profile": {"name": u.name, "email": u.email}} for u in users],
        "count": len(users),
        "version": "2.0"
    })
```

**Deprecation Timeline:**
- Day 1: Deploy v2, announce v1 deprecation with 90-day timeline
- Day 30: Log warnings when v1 endpoints are used
- Day 60: Email remaining v1 users with migration guide
- Day 90: Return 410 Gone from v1 endpoints

### Feature Flags
**Strategy:** Deploy new code but control activation with flags.

```python
from feature_flags import is_enabled

def process_payment(user_id, amount):
    if is_enabled('new_payment_processor', user_id):
        # New implementation
        return new_payment_processor.charge(user_id, amount)
    else:
        # Old implementation (fallback)
        return legacy_payment_processor.charge(user_id, amount)
```

**Rollout Plan:**
- 1% of users: Internal employees and beta testers
- 10% of users: Low-value transactions (<$10)
- 50% of users: Monitor for 24 hours
- 100% of users: Full rollout if metrics are green

---

## Step 5: Testing Strategies

### Blue-Green Deployment
**Setup:**
- Blue environment: Current production version
- Green environment: New version with migration

**Process:**
1. Deploy new version to green environment
2. Run smoke tests against green environment
3. Switch load balancer to send 10% traffic to green
4. Monitor error rates, latency, resource usage for 1 hour
5. If green, gradually increase traffic: 25% → 50% → 100%
6. Keep blue environment running for 24 hours as instant rollback option

**Rollback:**
```bash
# Instant rollback by switching load balancer
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TARGET_GROUP
```

### Canary Deployment
**Setup:**
- Canary: Small subset of servers (5-10%) running new version
- Main fleet: Majority of servers on current version

**Process:**
1. Deploy to canary servers
2. Monitor canary metrics vs main fleet for 2 hours
3. Compare error rates: `canary_errors / canary_requests` vs `main_errors / main_requests`
4. Compare latencies: p50, p95, p99 for canary vs main
5. If canary metrics within 5% of main fleet, proceed with full rollout

**Automated Canary Analysis:**
```python
def analyze_canary(canary_metrics, main_metrics):
    # Error rate comparison
    canary_error_rate = canary_metrics.errors / canary_metrics.requests
    main_error_rate = main_metrics.errors / main_metrics.requests
    
    if canary_error_rate > main_error_rate * 1.05:
        return "ROLLBACK: Canary error rate 5% higher than main fleet"
    
    # Latency comparison
    if canary_metrics.p95_latency > main_metrics.p95_latency * 1.2:
        return "ROLLBACK: Canary p95 latency 20% slower than main fleet"
    
    return "PROCEED: Canary metrics within acceptable range"
```

### Shadow Mode Testing
**Setup:**
- Production traffic duplicated to new system
- New system processes requests but responses discarded
- Only old system responses returned to users

**Implementation:**
```python
@app.route('/api/process', methods=['POST'])
def process_request():
    data = request.get_json()
    
    # Process with old system (returned to user)
    old_result = old_system.process(data)
    
    # Also process with new system in background (not returned)
    threading.Thread(target=shadow_process, args=(data,)).start()
    
    return jsonify(old_result)

def shadow_process(data):
    try:
        new_result = new_system.process(data)
        # Compare results
        if new_result != old_result:
            logger.warning(f"Shadow mode discrepancy: {data}")
    except Exception as e:
        logger.error(f"Shadow mode error: {e}")
```

**Benefits:**
- Test new system with real production traffic
- No user impact if new system has bugs
- Identify discrepancies before switching over

---

## Step 6: Common Migration Failures

### Failure 1: Database Connection Pool Exhaustion
**Symptom:** App crashes with "too many connections" after migration.

**Cause:** New ORM library has different connection pooling defaults.

**Solution:**
```python
# Old: SQLAlchemy 1.x default pool size: 5
engine = create_engine('postgresql://...')

# New: SQLAlchemy 2.x requires explicit pool configuration
engine = create_engine(
    'postgresql://...',
    pool_size=20,  # Increased from default 5
    max_overflow=10,  # Allow 10 additional connections under load
    pool_pre_ping=True  # Verify connections before use
)
```

### Failure 2: Serialization Format Changes
**Symptom:** Cached data causes deserialization errors after upgrade.

**Cause:** Library changed internal serialization format (e.g., pickle protocol version).

**Solution:**
```python
# Before migration: Clear all caches
redis_client.flushall()

# Or: Add version prefix to cache keys
def cache_key(name, version='v2'):
    return f"{version}:{name}"

# Migration strategy: Double-write with version prefix
cache.set(cache_key('user:123', 'v1'), old_format_data)
cache.set(cache_key('user:123', 'v2'), new_format_data)
```

### Failure 3: Race Conditions in Dual-Write
**Symptom:** Data inconsistency between old and new system during migration.

**Cause:** Writes to old system succeed but new system fails, or vice versa.

**Solution:**
```python
from contextlib import contextmanager

@contextmanager
def atomic_dual_write():
    old_transaction = old_db.begin_transaction()
    new_transaction = new_db.begin_transaction()
    
    try:
        yield (old_transaction, new_transaction)
        old_transaction.commit()
        new_transaction.commit()
    except Exception as e:
        old_transaction.rollback()
        new_transaction.rollback()
        raise e

# Usage
with atomic_dual_write() as (old_tx, new_tx):
    old_tx.execute("INSERT INTO users ...")
    new_tx.execute("INSERT INTO users ...")
```

### Failure 4: Dependency Conflicts
**Symptom:** `pip install` or `npm install` fails with conflicting version requirements.

**Cause:** Upgrading package A requires version 2.x of package C, but package B requires version 1.x of package C.

**Solution:**
```bash
# Python: Use dependency resolver to find compatible versions
pip install pip-tools
pip-compile --upgrade --resolver=backtracking requirements.in

# Or: Upgrade conflicting dependencies together
pip install 'packageA>=2.0' 'packageB>=3.0' --upgrade

# Node.js: Use npm overrides (package.json)
{
  "overrides": {
    "package-c": "2.0.0"
  }
}
```

### Failure 5: Memory Leaks in New Version
**Symptom:** Memory usage grows continuously after migration, eventually causing OOM crashes.

**Cause:** New library version has memory leak or your code uses new API incorrectly.

**Solution:**
```python
# Add memory profiling before and after migration
from memory_profiler import profile

@profile
def process_data(items):
    results = []
    for item in items:
        result = expensive_operation(item)
        results.append(result)
    return results

# Compare memory usage:
# Old version: 50MB baseline, grows to 80MB, drops back to 50MB after GC
# New version: 50MB baseline, grows to 200MB, never drops (LEAK!)

# Fix: Ensure proper resource cleanup
def process_data_fixed(items):
    results = []
    for item in items:
        result = expensive_operation(item)
        results.append(result)
        # Explicitly clean up if new API requires it
        result.cleanup()
    return results
```

### Failure 6: Authentication Token Format Changed
**Symptom:** All users logged out after migration; existing sessions invalid.

**Cause:** JWT library changed default algorithm or added required claims.

**Solution:**
```python
# Strategy 1: Support both old and new token formats during transition
def verify_token(token):
    try:
        # Try new format first
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        # Fall back to old format
        return jwt.decode(token, SECRET_KEY, algorithms=['HS512'])

# Strategy 2: Refresh all tokens before migration
# Send email to all users: "Please log in again in the next 7 days"
# Delete tokens older than 7 days before deploying new version
```

### Failure 7: API Response Time Regression
**Symptom:** p95 latency increases from 200ms to 2000ms after migration.

**Cause:** New ORM version has different query optimization behavior.

**Solution:**
```python
# Enable query logging to identify slow queries
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Example: N+1 query problem introduced by new ORM
# Old (fast): Single query with JOIN
users = db.query(User).join(Profile).all()

# New (slow): Separate query for each user's profile
users = db.query(User).all()
for user in users:
    profile = db.query(Profile).filter_by(user_id=user.id).first()  # N+1!

# Fix: Use eager loading
users = db.query(User).options(joinedload(User.profile)).all()
```

### Failure 8: File Encoding Issues After Language Upgrade
**Symptom:** Internationalized text displays as garbage characters after Python 2 → 3 migration.

**Cause:** Python 2 defaulted to ASCII, Python 3 defaults to UTF-8.

**Solution:**
```python
# Python 2 code (implicit ASCII encoding)
with open('data.txt', 'r') as f:
    content = f.read()  # ❌ Fails on non-ASCII characters

# Python 3 fix: Explicit UTF-8 encoding
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()  # ✓ Handles international characters

# Migration script to fix all existing files
import glob
for filepath in glob.glob('**/*.txt', recursive=True):
    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
```

### Failure 9: Integer Division Behavior Change
**Symptom:** Calculations produce different results after migration.

**Cause:** Python 2 used floor division by default, Python 3 uses true division.

**Solution:**
```python
# Python 2 behavior
result = 5 / 2  # Returns 2 (floor division)

# Python 3 behavior
result = 5 / 2  # Returns 2.5 (true division)

# Fix: Use explicit floor division
result = 5 // 2  # Returns 2 (works in both Python 2 and 3)

# Or: Import future division in Python 2 before migrating
from __future__ import division
result = 5 / 2  # Returns 2.5 (same as Python 3)
```

---

## Step 7: Timeline Estimation

### Small Migration (1-3 days)
**Examples:**
- Patch version upgrade with no breaking changes
- Single dependency update
- Configuration file format change

**Breakdown:**
- Planning: 2 hours
- Implementation: 4 hours
- Testing: 4 hours
- Deployment: 2 hours
- Monitoring: 4 hours

### Medium Migration (1-2 weeks)
**Examples:**
- Minor version framework upgrade
- Database schema change affecting <10 tables
- Migration with documented upgrade path

**Breakdown:**
- Planning: 1 day
- Implementation: 3 days
- Testing: 2 days
- Staging deployment: 1 day
- Production deployment: 1 day
- Monitoring and fixes: 2 days

### Large Migration (3-8 weeks)
**Examples:**
- Major version framework upgrade (React 17→18, Django 3→4)
- Database platform switch (MongoDB→PostgreSQL)
- Architecture change (monolith→microservices)

**Breakdown:**
- Research and planning: 1 week
- Implementation: 3 weeks
- Testing and validation: 2 weeks
- Gradual rollout: 1 week
- Monitoring and stabilization: 1 week

---

## Step 8: Automation Tools

### Migration Scripts
**Database Migrations:**
- **Alembic** (Python/SQLAlchemy): Version-controlled schema changes
- **Flyway** (Java): Database migration tool with rollback support
- **migrate** (Go): Database migration library
- **Liquibase** (Multi-language): Database schema change management

**Code Transformation:**
- **2to3** (Python): Automated Python 2 → 3 code conversion
- **jscodeshift** (JavaScript): Automated code refactoring tool
- **gofmt** (Go): Automatic code formatting and simple refactoring
- **rust-analyzer** (Rust): Automated refactoring and migration suggestions

### Testing Tools
- **Artillery**: Load testing to verify performance after migration
- **Locust**: Python-based load testing framework
- **k6**: Modern load testing tool with Grafana integration
- **Chaos Monkey**: Inject failures to test resilience of migrated system

### Monitoring Tools
- **Grafana + Prometheus**: Metrics dashboards comparing pre/post migration
- **Datadog**: APM and infrastructure monitoring
- **New Relic**: Application performance monitoring
- **Sentry**: Error tracking and alerting

---

## Real Migration Examples

### Example 1: React Class Components → Hooks
**Scope:** 47 class components → functional components with hooks

**Before:**
```javascript
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { user: null, loading: true };
  }

  componentDidMount() {
    fetch(`/api/users/${this.props.userId}`)
      .then(res => res.json())
      .then(user => this.setState({ user, loading: false }));
  }

  render() {
    if (this.state.loading) return <div>Loading...</div>;
    return <div>{this.state.user.name}</div>;
  }
}
```

**After:**
```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(user => {
        setUser(user);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}
```

**Timeline:** 2 weeks (automated codemod + manual fixes + testing)

### Example 2: MongoDB → PostgreSQL
**Scope:** 8 collections → 12 relational tables

**Strategy:**
1. Dual-write: Write to MongoDB and PostgreSQL simultaneously
2. Backfill: Migrate historical data in batches overnight
3. Validation: Compare MongoDB and PostgreSQL data for consistency
4. Switch reads: Change application to read from PostgreSQL
5. Deprecate MongoDB: Stop dual-write, keep MongoDB as backup for 30 days

**Timeline:** 6 weeks

**Code Changes:**
```python
# Before: MongoDB
user = db.users.find_one({"email": email})

# After: PostgreSQL
from sqlalchemy.orm import Session
user = session.query(User).filter(User.email == email).first()
```

### Example 3: Python 3.8 → 3.12
**Scope:** Entire codebase (50,000 lines)

**Breaking Changes:**
- `asyncio.get_event_loop()` deprecated → use `asyncio.run()`
- `typing` improvements: Use `list[str]` instead of `List[str]`
- `distutils` removed → migrate to `setuptools`

**Timeline:** 1 week

**Automation:**
```bash
# Use pyupgrade to automatically fix syntax
pyupgrade --py312-plus **/*.py

# Update type hints
find . -name "*.py" -exec sed -i 's/List\[/list[/g' {} \;
find . -name "*.py" -exec sed -i 's/Dict\[/dict[/g' {} \;
```

---

## Communication Plan Template

### Pre-Migration Announcement
**Subject:** [Action Required] Upcoming Migration: [System Name] on [Date]

**Body:**
```
Hi team,

We will be migrating [System Name] from [Old Version] to [New Version] on [Date] at [Time].

WHAT'S CHANGING:
- [Feature 1]: New behavior description
- [Feature 2]: New behavior description

WHY:
- [Reason 1: Security patch for CVE-XXXX-YYYY]
- [Reason 2: Performance improvement of 50%]

IMPACT:
- Expected downtime: [X minutes] from [Time] to [Time]
- Breaking changes: [List any API changes]
- Action required: [Any steps users need to take]

TESTING:
The new version is available in staging at [URL] for testing.

ROLLBACK PLAN:
If critical issues arise, we can rollback within 15 minutes.

QUESTIONS:
Reply to this email or join the #migration-discussion Slack channel.

Thanks,
[Your Name]
```

### Post-Migration Summary
**Subject:** [Completed] Migration: [System Name]

**Body:**
```
Hi team,

Migration of [System Name] completed successfully at [Time].

RESULTS:
- Downtime: [Actual minutes vs estimated]
- Issues encountered: [None / List of issues and resolutions]
- Performance: [Metrics comparison]

WHAT'S NEXT:
- Monitoring for 24 hours to ensure stability
- Please report any unexpected behavior to #support

ROLLBACK:
Old version remains available for 24 hours as backup.

METRICS:
- Error rate: [Before vs After]
- Response time: [Before vs After]
- Resource usage: [Before vs After]

Thanks for your patience during the migration.

[Your Name]
```
