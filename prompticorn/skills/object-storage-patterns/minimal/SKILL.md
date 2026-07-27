# Object Storage Patterns (Minimal)

## Purpose
Use object storage (S3, GCS, Blob) for what it is — a flat, HTTP key-value store of immutable blobs — and stop treating it like a filesystem.

## Core Techniques

### 1. It Is Not a Filesystem
There are no real directories, no cheap rename, no in-place append. A "folder" is just a key prefix. Renaming or moving means copy-then-delete (a full rewrite). Editing means rewriting the whole object. Design for write-once, read-many; never for the mutate-in-place patterns a POSIX filesystem makes cheap.
```
# "path/to/file.txt" is one flat key, not a tree walk
bucket:  my-data
key:     year=2026/month=07/events.parquet   # prefix is convention, not a dir
```

### 2. Know Your Consistency Model
Modern object stores give strong read-after-write for new objects: PUT then GET returns the data. But overwrites and deletes can still surface subtle staleness, and *listing* may lag a just-written object. Never use a bucket LIST as a source of truth for "does this exist right now" in a tight loop — track state in a database and use storage for the bytes.

### 3. Match the Storage Class to Access Frequency
| Tier | Access pattern | Trade-off |
|---|---|---|
| Standard / hot | Frequent reads | Highest storage price, no retrieval fee |
| Infrequent-access | Read rarely, need it fast | Cheaper storage, per-GB retrieval fee + min duration |
| Archive / cold | Rare, tolerate delay | Cheapest storage, retrieval latency + fee |
The retrieval fee is the trap: put frequently-read data in a cold tier and per-request charges dwarf the storage savings.

### 4. Automate Lifecycle Transitions
Do not move objects by hand. Write lifecycle rules that transition by age and expire what is dead, so cost tracks the data's actual value over time.
```
rule: logs/*   ->  IA after 30d  ->  Archive after 90d  ->  delete after 365d
```

### 5. Keep Buckets Private; Grant Access by URL or Role
Default-deny public access. Serve to browsers with time-limited pre-signed URLs (a signed key granting temporary read/write to one object), and grant services access by IAM role, not by making the bucket public. A public bucket is the classic data-leak headline.

### 6. Design Keys for Access and Scale
The key layout is your only index. Prefix by the dimension you query/list on (date, tenant). Modern stores auto-scale request throughput, but a good prefix scheme still governs listing cost and how cleanly lifecycle rules and access policies apply.
```
tenant=42/date=2026-07-27/type=invoice/<id>.json   # lists, rules, IAM all scope cleanly
```

### 7. Front Reads With a CDN
Object storage bills every GET as a request plus egress. For anything read repeatedly and served to users — images, downloads, static sites — put a CDN in front (see **edge-and-cdn-delivery**) so repeat reads hit the edge instead of billing an origin GET each time. Encrypt at rest and enforce TLS in transit by policy.

## Warning Signs
- Code that renames/moves objects expecting it to be cheap (it is a full copy)
- Appending to an object, or rewriting a huge object to change a few bytes
- A bucket LIST used as the authoritative "does X exist" check
- Everything left in the hot tier, or cold-tiered data that is read constantly
- Manual cleanup instead of lifecycle rules; buckets that only grow
- A public bucket, or long-lived credentials handed to browsers instead of pre-signed URLs
- All objects under one flat prefix, making listing and lifecycle scoping painful
