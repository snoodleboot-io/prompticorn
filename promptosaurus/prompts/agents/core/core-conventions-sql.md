<!-- path: promptosaurus/prompts/agents/core/core-conventions-sql.md -->
# Core Conventions SQL

Database:            {{DATABASE}}           e.g., PostgreSQL, MySQL, SQLite
ORM/Query:           {{ORM_QUERY_BUILDER}}                e.g., Prisma, SQLAlchemy, GORM, Drizzle

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Mutation:       {{MUTATION_COVERAGE_%}}       e.g., 80%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests (Query Tests)
- Test individual queries, stored procedures, functions
- Use assertions on query results
- Test edge cases: empty results, nulls, boundaries

##### Integration Tests
- Test at service or module boundary
- Use transactions with rollback for isolation
- Test migrations, triggers, constraints

##### Schema Tests
- Verify constraints are enforced
- Test foreign key relationships
- Test indexes are used correctly (EXPLAIN ANALYZE)

##### Data Migration Tests
- Test migration up/down
- Verify data integrity after migration
- Test rollback procedures

##### Performance Tests
- Test query performance with EXPLAIN ANALYZE
- Verify indexes are used
- Test under load with realistic data volumes

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., pytest, Go test, Jest
Mocking library: {{MOCKING_LIBRARY}}              e.g., factory_boy, testfixtures
Coverage tool:  {{COVERAGE_TOOL}}              e.g., coverage.py, istanbul
Factory tool:   {{FACTORY_TOOL}}          e.g., factory_boy, testdata

#### Scaffolding

```python
# Python example with pytest
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("postgresql://test:test@localhost/testdb")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_user_query(db_session):
    result = db_session.execute("SELECT * FROM users WHERE id = 1")
    assert result.fetchone() is not None
```

```bash
# Run with coverage
pytest --cov --cov-report=html
```

##### CI Integration
```yaml
# GitHub Actions example
- name: Run SQL tests
  run: |
    docker-compose up -d test-db
    pytest tests/sql/ --cov
    docker-compose down
```

## SQL-Specific Rules

### Query Safety
- Parameterized queries always — never interpolate strings into SQL
- Use prepared statements for repeated queries
- Never use `SELECT *` — specify columns explicitly

### Migrations
- Always include both `up` and `down` migrations
- Use descriptive migration names: `add_users_table.sql`
- Never modify existing migrations — create new ones to fix
- Add indexes in migrations, not after

### Schema Design
- Use explicit primary keys (UUID or auto-increment)
- Add `created_at` and `updated_at` timestamps to all tables
- Use constraints: NOT NULL, UNIQUE, CHECK, FOREIGN KEY
- Avoid nullable columns where possible

### Naming Conventions
- Tables: `snake_case`, plural (`users`, `order_items`)
- Columns: `snake_case` (`user_id`, `created_at`)
- Indexes: `idx_<table>_<columns>`
- Foreign keys: `fk_<table>_<referenced_table>`

### Performance
- Index any column used in WHERE or JOIN
- Use EXPLAIN ANALYZE to verify query plans
- Avoid functions on indexed columns in WHERE clauses
- Use connection pooling (PgBouncer, etc.)

### Testing
- Use transactions with rollback for test isolation
- Seed test data consistently
- Use factory patterns for test data creation
