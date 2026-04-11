# Data Streaming Subagent (Verbose)

**Focus:** Comprehensive real-time data processing and streaming architectures

## Overview

Stream processing handles continuous, unbounded data flows. Unlike batch processing (finite datasets), streams are conceptually infinite, requiring different thinking about time, state, and correctness.

## When to Use

- **Real-time analytics** - Metrics that update continuously
- **Event-driven systems** - React immediately to events
- **Monitoring and alerting** - Detect issues as they occur
- **Real-time personalization** - Recommendations updated instantly
- **Fraud detection** - Identify suspicious patterns in real-time
- **Complex event processing** - Detect patterns across events
- **Stream enrichment** - Join streaming data with reference tables
- **Aggregations over time** - Running counts, averages, percentiles
- **Deduplication** - Remove duplicate events
- **State management** - Remember past values across time
- **Exactly-once processing** - No data loss, no duplicates
- **Backpressure handling** - Source faster than processing

## Core Competencies

### Time Concepts

**Event Time:**
- When the event actually occurred (timestamp in event)
- What we care about for analysis
- Can arrive out of order or late
- Example: User clicked at 10:00 AM, but arrives in system at 10:05 AM

**Processing Time:**
- When system processes the event
- System clock time
- Unreliable (depends on processing delays)
- Simple but wrong for most use cases

**Watermark:**
- Indicator of progress through event time
- "We've processed all events up to timestamp X"
- Allows system to close windows and emit final results
- Handles late data: events arriving after watermark considered late

**Use Event Time!**
```python
# WRONG - based on processing time
SELECT SUM(amount) OVER (ROWS BETWEEN 300 PRECEDING AND CURRENT ROW)

# RIGHT - based on event time with watermark
SELECT SUM(amount) OVER (
  PARTITION BY user_id
  ORDER BY event_time
  RANGE BETWEEN INTERVAL 5 MINUTES PRECEDING AND CURRENT ROW
)
```

### Windowing Strategies

**Tumbling Window:**
- Fixed-size, non-overlapping windows
- Example: 5-minute buckets (00-05, 05-10, 10-15)
- Use for: Hourly reports, minute-level aggregates

```
Event at 10:03 → goes into [10:00-10:05)
Event at 10:05 → goes into [10:05-10:10)
Event at 10:07 → goes into [10:05-10:10)
```

**Sliding Window:**
- Fixed-size, overlapping windows
- Example: 5-minute window that slides every minute
- Use for: Moving averages, SMA

```
Events at 10:00, 10:01, 10:02, 10:03, 10:04
  [10:00-10:05) has: 00, 01, 02, 03, 04
[10:01-10:06) has: 01, 02, 03, 04 (+ future 05)
  [10:02-10:07) has: 02, 03, 04 (+ future 05, 06)
```

**Session Window:**
- Variable-size, event-driven windows
- Groups events with gap timeout
- Use for: User sessions, related activity bursts

```
Events: 10:00, 10:02, 10:03, 10:30, 10:32
With 5-minute gap:
  Session 1: [10:00-10:03] (gap < 5m)
  [Gap 27m]
  Session 2: [10:30-10:32] (gap < 5m)
```

### State Management

**Stateless Operations:**
- Map, filter, project
- No memory of past
- Highly scalable
- Example: Extract customer_id from event

**Stateful Operations:**
- Remember values across time
- Examples: Running sums, joins, deduplication
- Need to manage state store
- Requires fault tolerance (checkpoint state)

**State Patterns:**

**Keyed State:**
```python
# Remember last value per customer
for event in stream:
    customer_id = event.customer_id
    state[customer_id] = event.value  # Store per key
    
# Later when new event arrives
customer_value = state[customer_id]  # Retrieve previous value
```

**Global Aggregation:**
```python
# Sum across all events (no key)
total = 0
for event in stream:
    total += event.amount
```

**Windowed State:**
```python
# Aggregate within windows
for event in stream:
    window = event.timestamp.round_to_minute()
    window_state[window] += event.amount
    
# When window closes, emit result and delete state
```

### Exactly-Once Semantics

**Problem:**
- Network can lose messages
- Processing can crash and restart
- Naive approach: Reprocess → duplicates

**Solutions:**

**Idempotent Writes:**
```python
# Use unique ID, can safely reprocess
UPDATE users SET last_login = now() WHERE id = user_id
# Reprocessing same event updates same row (no duplicate)
```

**Transactional Writes:**
```python
# Atomic: all succeed or all fail
BEGIN TRANSACTION
  Write to warehouse
  Update processing checkpoint
COMMIT
```

**Deduplication:**
```python
# Keep IDs of processed events
if event_id not in processed_events:
    process(event)
    processed_events.add(event_id)
```

**Checkpointing (Flink approach):**
```
Kafka offset 1000
  ↓ (process events)
State updated to X
  ↓ (atomically checkpoint)
Kafka offset + State X saved together
  ↓ (crash)
On restart: Resume from checkpoint
  Kafka resumes from offset 1000
  State restores to X
  No duplicates, no loss
```

### Late & Out-of-Order Data

**Out-of-Order:**
```
Event 1: Click at 10:00 (arrives 10:00)
Event 2: Click at 10:05 (arrives 10:01 - out of order!)
```

**Late Data:**
```
Event: Click at 10:00 (arrives 10:10 - 10 minutes late)
```

**Handling Strategies:**

**Watermark-based:**
```
Process events until watermark
Watermark says "all events up to 10:00 processed"
Event arriving at 10:03 with timestamp 10:00 is LATE
Options:
  - Ignore (discard)
  - Allow (update window, re-emit)
  - Side output (send to separate stream for review)
```

**Grace Period:**
```
Window [10:00-10:05)
Watermark reaches 10:10
Grace period: 5 minutes
Late events accepted until 10:15
Event at 10:06 timestamp:
  - Arrives at 10:12: Accepted (within grace)
  - Arrives at 10:17: Rejected (beyond grace)
```

**Trade-offs:**
- Longer grace period: Correct results but delayed output
- Shorter grace period: Fast results but may miss late data
- No grace period: Fast but incorrect

### State Store Management

**In-Memory State:**
- Fast access
- Lost on crash
- Limited by RAM

**Persistent State (RocksDB, etc):**
- Survives crashes
- Disk I/O overhead
- Can be very large

**Remote State (Redis, etc):**
- Shared across tasks
- Network latency
- External dependency

**Choosing:**
- Small state → In-memory
- Critical state → Persistent with backup
- Shared state → Remote store
- Performance critical → Caching layer

### Backpressure & Scaling

**Backpressure Problem:**
```
Source: 1 million events/sec
Processor: Can handle 100k events/sec
Result: Queue overflows, memory explodes
```

**Solutions:**
- Buffer (queue fills, then blocks source)
- Slow down source (feedback)
- Scale up processing (add more tasks)
- Drop events (sample if acceptable)

**Implementing:**
- Most frameworks handle automatically
- Monitor lag (how far behind real-time?)
- Alert when lag grows
- Scale when lag > threshold

### Stream Processing Frameworks

**Apache Flink:**
- Pros: Powerful, exactly-once, event time, low latency
- Cons: Operational complexity, JVM overhead
- Use when: Need powerful features, tolerating complexity

**Apache Kafka Streams:**
- Pros: Simple, stateless-friendly, no external service
- Cons: Limited state management, scaling more complex
- Use when: Simple pipelines, embedded processing

**Spark Structured Streaming:**
- Pros: SQL-friendly, unified batch/stream, good integration
- Cons: Micro-batch latency, not true streaming
- Use when: Data engineers prefer SQL, latency not critical

**Cloud-native (Kinesis, Pub/Sub, EventHub):**
- Pros: Managed, less operational burden
- Cons: Vendor lock-in, pricing based on throughput
- Use when: Want managed service, not cost-sensitive

## Stream Processing Patterns

**Event Enrichment:**
```
Raw event → Join with reference table → Enriched event
```

**Deduplication:**
```
Events with IDs → Track seen IDs → Deduplicated stream
```

**Session Windows:**
```
User clicks → Group by user + session gap → Sessions
```

**Anomaly Detection:**
```
Metrics → Compare to baseline → Flag deviations
```

**Complex Event Processing:**
```
Stream of events → Pattern matching → Alert on pattern match
```

## Common Mistakes

- **Using processing time instead of event time** - Incorrect results
- **Ignoring out-of-order data** - Data loss or corruption
- **No state checkpointing** - Lose correctness on crash
- **Unbounded state growth** - Memory leak
- **No monitoring** - Silent failures
- **Scaling after pipeline full** - Too late
- **Ignoring watermarks** - Wrong window closing
- **Blocking operations** - Kills throughput

## Monitoring Stream Health

- **End-to-end latency** - Event time to output
- **Processing lag** - How far behind real-time?
- **Throughput** - Events/sec processed
- **Backpressure** - Queue sizes, buffer utilization
- **State size** - Memory and disk usage
- **Error rate** - Failed events
- **Checkpoint latency** - How long to checkpoint?
- **Partition lag** - Lag by partition (skew detection)
