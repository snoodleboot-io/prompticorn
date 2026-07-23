# Distributed Caching Design (Minimal)

## Purpose
Add a shared cache that actually reduces load and latency, without serving stale data or collapsing the origin the moment the cache misses.

## Core Techniques

### 1. Pick the Write Strategy Deliberately

| Strategy | Write path | Staleness | Failure mode |
|---|---|---|---|
| Cache-aside | App writes DB, deletes key | Bounded by TTL and races | Miss storm on cold cache |
| Write-through | App writes cache, cache writes DB | None | Cache outage blocks writes |
| Write-behind | App writes cache, flushed async | None on read | Data loss if cache dies before flush |
| Read-through | Cache library fetches on miss | Same as cache-aside | Hides misses from your metrics |

Cache-aside is the default because it degrades well: if the cache is down, every read still succeeds against the database, just slower. Write-through couples your write availability to the cache — the cache is now on the critical path for correctness, not just speed. Write-behind trades durability for latency and is only acceptable for data you can afford to lose.

On write, **delete the key rather than updating it**. Updating races: two concurrent writers can interleave so the cache ends up holding the older value permanently. A delete forces the next reader to re-derive from the source of truth.

### 2. Do Not Rely on TTL Alone for Correctness

A TTL is a bound on *how long* you serve stale data, not a mechanism for avoiding it. With a 5-minute TTL and no invalidation, a price change is wrong for up to 5 minutes for every reader. That is fine for a leaderboard and unacceptable for an account balance.

Rule of thumb: TTL is a safety net for keys you forgot to invalidate and for cache-size control. Explicit invalidation on write is what gives you correctness. Use both.

### 3. Defend Against the Thundering Herd

A hot key expires; 5,000 concurrent requests all miss and all hit the database with the same query. The database saturates, latency climbs, more requests pile up.

Two fixes, both worth having:

**Request coalescing** — one caller recomputes, the rest wait for that result.

```python
def get(key):
    if (v := cache.get(key)) is not None:
        return v
    if cache.set(f"lock:{key}", token, nx=True, ex=10):   # only one winner
        try:
            v = load_from_db(key)
            cache.setex(key, 300, v)
            return v
        finally:
            cache.delete(f"lock:{key}")
    time.sleep(0.05)                    # loser briefly waits, then re-reads
    return cache.get(key) or load_from_db(key)
```

**Probabilistic early expiry** — each reader independently decides to refresh slightly early, so the recompute spreads out instead of landing on one instant.

```python
# refresh early with probability rising as the entry ages
if remaining_ttl < delta * beta * -math.log(random.random()):
    refresh_async(key)
```

Also jitter your TTLs. Setting 3600 everywhere means keys written together expire together.

### 4. Handle the Miss You Cannot Cache

Requests for keys that do not exist bypass the cache every time — a cheap denial of service. Cache the negative result too, with a short TTL (30–60s), or put a Bloom filter in front for known-existent ids.

### 5. Key Design Determines Invalidation Cost

```
user:8812:profile:v3
```

Include an entity type, the id, and a schema version. The version segment means a deploy that changes the serialized shape invalidates everything by bumping one constant — far safer than a `SCAN`-and-delete sweep across a live keyspace. Never build keys from unbounded input (raw query strings) unless you hash them; cardinality is what fills a cache with entries read exactly once.

### 6. Measure Hit Rate Per Key Class, Not Globally

A global 95% hit rate hides a 20% hit rate on the class doing all the database damage. Break the metric down by key prefix, and track origin load — the number the cache exists to reduce — alongside it.

## Warning Signs

- Cache updated in place on write instead of invalidated
- One TTL constant used everywhere, with no jitter
- No single-flight or early-expiry protection on hot keys
- Misses for nonexistent keys reaching the database unbounded
- Hit rate reported only as a global aggregate
- Application logic that breaks when the cache returns a miss
- Serialized objects cached without a schema version in the key
- Cache used as the source of truth for anything you cannot rebuild
