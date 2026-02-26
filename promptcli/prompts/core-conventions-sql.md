# SQL Conventions

Database:            {{DATABASE}}           e.g., PostgreSQL, MySQL, SQLite
ORM/Query:           {{ORM}}                e.g., Prisma, SQLAlchemy, GORM, Drizzle

## Testing
Framework:           {{TEST_FRAMEWORK}}     e.g., pytest, Go test, Jest
Coverage target:      {{COVERAGE_%}}         e.g., 80%
Mocking library:     {{MOCK_LIB}}           e.g., factory_boy, testfixtures

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
