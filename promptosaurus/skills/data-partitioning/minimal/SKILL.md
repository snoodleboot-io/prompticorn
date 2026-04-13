# Data Partitioning (Minimal)

## Key Strategies

### Time-Based Partition
```sql
CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  amount DECIMAL
) PARTITION BY RANGE (YEAR(created_at)) (
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION p2025 VALUES LESS THAN (2026),
  PARTITION p2026 VALUES LESS THAN (2027)
);
```

Benefits: Quick date-range queries, easy archival

### Range Partition
```sql
CREATE TABLE events (
  event_id INT,
  user_id INT
) PARTITION BY RANGE (user_id) (
  PARTITION p1 VALUES LESS THAN (1000000),
  PARTITION p2 VALUES LESS THAN (2000000),
  PARTITION p3 VALUES LESS THAN (MAXVALUE)
);
```

### List Partition
```sql
PARTITION BY LIST (region) (
  PARTITION p_us VALUES IN ('US-EAST', 'US-WEST'),
  PARTITION p_eu VALUES IN ('EU-WEST', 'EU-CENTRAL'),
  PARTITION p_apac VALUES IN ('APAC-EAST', 'APAC-SOUTH')
);
```

## Query Performance
- Partition pruning: Only scan relevant partition
- 10B rows split into 10 partitions = 1B rows per partition
- Queries 10x faster

## Maintenance
- Archive old partitions (2020 data to cold storage)
- Add new partitions automatically
- Monitor partition sizes
