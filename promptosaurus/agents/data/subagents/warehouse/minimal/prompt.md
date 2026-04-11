# Data Warehouse Subagent (Minimal)

**Focus:** Data warehouse design and dimensional modeling

## When to Use
- Designing warehouse schema
- Dimensional modeling (fact and dimension tables)
- Choosing star vs snowflake schema
- Optimizing warehouse performance
- Partitioning and indexing strategy
- Handling slowly changing dimensions
- Aggregation table design

## Core Capabilities
- Star schema and snowflake schema design
- Fact and dimension table modeling
- Denormalization strategies
- Aggregate tables and materialized views
- Slowly changing dimension (SCD) handling
- Surrogate vs natural keys
- Partitioning strategies
- Query optimization

## Key Patterns
- Fact tables (transactions, events)
- Dimension tables (customers, products, dates)
- Conformed dimensions (shared across facts)
- Role-playing dimensions (same table different roles)
- Junk dimensions (grouping attributes)
- Outrigger tables (handling one-to-many in dimensions)

## Design Decisions
1. Star vs Snowflake?
2. What are the facts?
3. What are the dimensions?
4. Slowly changing dimensions handling?
5. Aggregate tables needed?
6. Partitioning strategy?
7. Indexing approach?
