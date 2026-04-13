---
name: dimensional-modeling
type: skill
category: technical-skill
minimal: true
---
# Dimensional Modeling (Minimal)

## Core Concepts

### Star Schema
```
                  Time
                   |
Product -----> Fact Table <----- Customer
                   |
                Geography
```

### Fact Table
Contains measurements/events:
- order_id, customer_id, product_id, date_id
- quantity, revenue, discount
- Foreign keys to dimensions

### Dimension Tables
Describe context:
- **Customer**: id, name, region, segment
- **Product**: id, name, category, brand
- **Date**: id, date, month, quarter, year

## Example

**Fact: Sales**
```sql
CREATE TABLE fact_sales (
  sale_id INT,
  customer_id INT,
  product_id INT,
  date_id INT,
  quantity INT,
  revenue DECIMAL
);
```

**Dimension: Customer**
```sql
CREATE TABLE dim_customer (
  customer_id INT PRIMARY KEY,
  name VARCHAR,
  segment VARCHAR
);
```

## Star vs Snowflake

**Star:** Denormalized (faster queries, simpler)
```
Fact -----> Dim_Customer
         |-> Dim_Product
```

**Snowflake:** Normalized (less redundancy)
```
Fact -----> Dim_Customer -----> Dim_Segment
```

## Benefits
- Fast queries (few joins)
- Intuitive (clear dimensions)
- Scalable (handles growth)
