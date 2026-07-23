# NoSQL Database Selection (Minimal)

## Purpose
Choose a non-relational store by starting from the queries you must serve, not
from the shape of your entities or a scale number you have not yet reached.

## Core Techniques

### 1. Enumerate Access Patterns First
Before naming any product, write every read and write the system performs, with
its shape, frequency, and latency budget:

| # | Access pattern | Shape | Rate | Budget |
|---|---|---|---|---|
| 1 | Get order by id | Point read | 4k/s | p99 < 10 ms |
| 2 | List a customer's orders, newest first, paged | Range on sorted key | 800/s | p99 < 30 ms |
| 3 | Orders in state SHIPPED older than 2 days | Filtered scan | 1/min | seconds ok |
| 4 | Revenue by region by month | Aggregation | 20/day | seconds ok |

Pattern 4 is not an OLTP query and does not belong in this store — send it to a
warehouse (see `dimensional-modeling`). Patterns 1 and 2 drive the key design.
Pattern 3 needs a secondary index or a sweep job. A store that cannot serve your
list of patterns is disqualified regardless of how good it looks in benchmarks.

### 2. Match Query Shape to Store Family
| Family | Good at | Bad at | Examples |
|---|---|---|---|
| Key-value | Point get/put by known key; very low latency | Any query not by key | Redis, Memcached |
| Document | Fetch a whole nested aggregate; flexible fields; secondary indexes | Multi-document joins, cross-doc transactions at scale | MongoDB, DocumentDB, Couchbase |
| Wide-column | Point + range reads on a designed key at very high write rates | Ad-hoc queries, joins, aggregation | Cassandra, ScyllaDB, DynamoDB, HBase |
| Graph | Multi-hop traversal, variable-depth paths, shortest path | Bulk scans, analytics over all nodes | Neo4j, Neptune |
| Time-series | Append-only writes; time-range rollups; retention/downsampling | Updates, joins, relational integrity | Timescale, InfluxDB, Prometheus |

Ask what the store cannot do before what it can. Elimination is faster and more
reliable than comparison.

### 3. Model the Queries, Not the Entities (DynamoDB Single-Table)
In a wide-column/KV store you cannot join, so you pre-join at write time by
placing related items under a shared partition key:

```
PK                SK                     attributes
CUSTOMER#42       PROFILE                name, email, tier
CUSTOMER#42       ORDER#2026-03-01#9912  total, status
CUSTOMER#42       ORDER#2026-02-17#9744  total, status
ORDER#9912        ITEM#1                 sku, qty, price
```

- Pattern 1 (get order) — get on `ORDER#9912`
- Pattern 2 (customer's orders, newest first) — query `PK = CUSTOMER#42` with
  `SK begins_with ORDER#`, descending; the profile and the orders come back in
  one request, no join
- Pattern 3 (by status) — a GSI keyed on `status` with the date as sort key

The sort key encodes the ordering you need, so it embeds the timestamp before
the id. This is why the technique is query-first: change the access patterns and
the key design changes, whereas a normalized model would not have to. Do not
adopt single-table design unless your patterns are known and stable — its cost
is exactly that rigidity.

### 4. Do Not Choose NoSQL for "Scale" Below a Few TB
A single well-indexed Postgres or MySQL instance on modern hardware handles
low tens of thousands of OLTP transactions per second and several TB comfortably,
with joins, transactions, and constraints you would otherwise reimplement in
application code. Most systems that "needed NoSQL for scale" needed an index.

Legitimate reasons to leave relational: write throughput beyond what one primary
can absorb, genuinely schemaless or highly variable documents, multi-region
active-active writes, single-digit-millisecond point reads at very high rates,
or an operational preference for a managed store with no capacity planning.
"We might grow" is not one of them.

### 5. Pick a Consistency Model on Purpose
| Model | Guarantee | What it breaks |
|---|---|---|
| Strong / linearizable | A read sees the latest committed write | Higher latency; unavailable during partitions |
| Eventual | Replicas converge, no ordering promise | Read-your-writes: a user edits, reloads, sees stale data |
| Causal | Related operations are seen in order | Concurrent unrelated writes still conflict |

Eventual consistency is fine for a product catalogue and wrong for an account
balance or an inventory decrement. Many stores let you choose per read, so pay
for strong reads only on the paths that need it.

## Warning Signs

- A store chosen before the access patterns were written down
- "We need NoSQL to scale" with no measured throughput or data-size number
- Application code joining documents in a loop — you needed a relational database
- Single-table design adopted while access patterns are still churning
- Aggregation and reporting queries running against the OLTP NoSQL store
- Eventual consistency on a balance, counter, or inventory path
- Unbounded partitions (all rows under one key) or a hot partition on a popular id
- A graph database holding data that is only ever queried one hop deep
