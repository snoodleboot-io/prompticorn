---
name: idempotency-patterns
type: skill
category: technical-skill
minimal: true
---
# Idempotency Patterns (Minimal)

## Definition
**Idempotent:** Same operation repeated = same result

Bad (not idempotent):
```python
account.balance += 100  # Repeat 3x = +300
```

Good (idempotent):
```python
account.balance = 1000  # Repeat 3x = 1000
```

## Natural Keys Pattern
```sql
-- Bad: Depends on auto-increment
INSERT INTO orders VALUES (NULL, customer_id, amount);
-- Retry creates duplicate!

-- Good: Use natural key (customer_id, timestamp)
INSERT OR REPLACE INTO orders (customer_id, order_time, amount)
VALUES (123, '2026-04-10 14:30:00', 99.99);
-- Retry is safe, replaces same row
```

## Idempotency Keys
```python
# Client generates unique ID for each request
response = api.create_order(
  customer_id=123,
  idempotency_key="order-123-2026-04-10-143000"
)

# Server:
# First request: Creates order, saves idempotency_key
# Retry request: Sees key exists, returns cached response
```

## Patterns
1. **INSERT OR REPLACE**: Upsert using natural key
2. **State Machine**: Check current state, validate transition
3. **Deduplication**: Track processed IDs, skip duplicates
4. **Version Numbers**: Optimistic locking prevents duplicates

## Golden Rule
Use natural business keys (customer_id, date), not synthetic IDs
