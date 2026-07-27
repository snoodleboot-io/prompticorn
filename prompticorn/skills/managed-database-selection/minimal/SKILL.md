# Managed Database Selection (Minimal)

## Purpose
Choose a managed database by the access pattern the data will actually see — not by which engine is most familiar or most talked about.

## Core Techniques

### 1. Start From the Access Pattern, Not the Data Model
Write down, before choosing anything: read/write ratio, query shapes (point lookup vs range scan vs join vs aggregate), item size, expected cardinality, and consistency needs. The pattern selects the family; the engine is a detail after that.

### 2. Map the Pattern to a Data Model Family
| Family | Fits when | Managed examples |
|---|---|---|
| Relational | Joins, transactions, ad-hoc queries, integrity matters | RDS/Aurora, Cloud SQL, Azure SQL |
| Document | Nested/variable-shape entities, read whole aggregate | DocumentDB, MongoDB Atlas, Firestore |
| Key-value | Known-key point lookups, very high throughput | DynamoDB, Bigtable, Memorystore |
| Wide-column | Huge write volume, partition-key access, time buckets | Cassandra/Keyspaces, Bigtable |
| Time-series | Append-heavy metrics/events, time-range rollups | Timestream, TimescaleDB, InfluxDB |
See **nosql-database-selection** for the deeper non-relational decision.

### 3. Default to Relational Until a Pattern Forces Otherwise
A relational engine lets you defer query design: normalize now, query many ways later. Non-relational stores make you commit to the access pattern up front (the partition key *is* the design). Reach for them when scale, write volume, or shape genuinely demands it — not preemptively.

### 4. Pick the Managed Tier for the Operational Shape
Within relational you still choose the operational model:
- **Instance-based** (RDS, Cloud SQL) — you pick instance size; predictable cost, you manage scaling.
- **Cloud-native / distributed** (Aurora, Spanner, AlloyDB) — storage/compute separated, scales reads via replicas, higher floor.
- **Serverless** (Aurora Serverless, DynamoDB on-demand) — scales to load, good for spiky or unpredictable traffic.

### 5. Design Replicas and Failover Deliberately
A read replica is not a backup and not automatic failover. Distinguish: read replicas (offload reads, may lag), multi-AZ standby (HA failover), and cross-region replicas (DR + locality). Async replicas can lag — do not read-after-write from one and expect consistency.

### 6. Let Consistency and Locality Drive the Choice
If you need strong global consistency, that narrows the field sharply (e.g. Spanner-class systems) and costs write latency, because a commit must reach a quorum across regions. If eventual consistency is acceptable, far more options open up and get cheaper. Decide this explicitly; do not discover it in production.

### 7. Absorb Read Load With a Cache, Not a Bigger Primary
Before scaling the primary vertically to serve read-heavy traffic, put a cache in front (see **distributed-caching-design**). It is cheaper, and it keeps the database sized for its write load rather than its read fan-out. Scale the engine only for writes it genuinely must handle.

## Warning Signs
- Engine chosen before the access pattern was written down
- A document or key-value store selected to "scale", then queried with joins and ad-hoc filters it cannot serve
- Relational schema forced into a key-value store, losing transactions and integrity
- Read replica treated as a backup, or as automatic failover
- Read-after-write against an async replica, then surprise at stale reads
- Provisioned instance sized for peak, idle most of the day, when serverless fit better
- Cross-region strong consistency assumed "for free"
