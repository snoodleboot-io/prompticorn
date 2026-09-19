# Vector Store Selection (Minimal)

## Purpose
Choose where embeddings live by starting from corpus size, filter requirements,
and re-embedding cadence — not from the assumption that vectors need a vector
database.

## Core Techniques

### 1. Default to a Relational Extension Until It Actually Hurts
Most teams reach for a dedicated vector database at a scale where a Postgres
extension would have been simpler and faster to operate. Below roughly a million
vectors, `pgvector` on the database you already run answers queries in tens of
milliseconds, joins to your metadata for free, and needs no new backup, upgrade,
or on-call story.

```sql
CREATE TABLE chunk (
  id         bigserial PRIMARY KEY,
  doc_id     bigint REFERENCES document(id),
  tenant_id  bigint NOT NULL,
  body       text,
  embedding  vector(768)
);
CREATE INDEX ON chunk USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

The join is the point. A dedicated store makes you keep the vector in one system
and the row it describes in another, and then reconcile them forever.

Real reasons to leave: more than tens of millions of vectors, sustained query
rates a shared OLTP primary cannot absorb alongside its normal load, or a need
to rebuild indexes continuously without touching the transactional database.
"We will have a lot of documents" is not one of them.

### 2. Pick the Index Type From the Recall Budget
| Index | Build cost | Query latency | Memory | Recall | Pick when |
|---|---|---|---|---|---|
| Flat (exact) | None | O(n) — ms at 100k, seconds at 10M | Vectors only | 100% | < ~100k vectors, or recall must be exact |
| IVF | Minutes; needs training on a sample | Fast, tunable via `nprobe` | Vectors + centroids | 90–98% typical | Large corpus, RAM-constrained, rebuilds tolerable |
| HNSW | Slow, incremental | Fastest at high recall | Vectors + graph, ~1.5–2× | 95–99%+ | Latency-critical, memory available, frequent inserts |

HNSW is the usual answer when memory allows; IVF is the answer when it does not.
Flat is the answer more often than people admit — it is also the ground truth you
measure the others against.

### 3. Measure Recall Against Exact Search Before Tuning Anything
Approximate indexes silently return the wrong neighbours. Compute exact top-k on
a sample, then measure what the index returns:

```python
def recall_at_k(index, exact_neighbors, queries, k=10) -> float:
    hits = 0
    for q, truth in zip(queries, exact_neighbors):
        got = set(index.search(q, k))
        hits += len(got & set(truth[:k]))
    return hits / (k * len(queries))
```

Then sweep the one knob that trades recall for latency — `ef_search` for HNSW,
`nprobe` for IVF — and pick the smallest value clearing your recall target. A
system tuned by eyeballing result quality is tuned to nothing.

### 4. Combine Lexical and Dense Retrieval
Dense vectors miss exact tokens: part numbers, error codes, rare proper nouns,
negations. BM25 misses paraphrase. Run both and fuse the ranks:

```python
def rrf(bm25_ids, dense_ids, k=60):          # reciprocal rank fusion
    scores = defaultdict(float)
    for ranked in (bm25_ids, dense_ids):
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

RRF needs no score normalization, which is its main advantage over a weighted
sum of cosine and BM25 scores that live on incomparable scales.

### 5. Filter Inside the Index, Not Around It
The trap has two sides, and both produce quiet quality failures:

- **Post-filter** — fetch top-100 by vector, then drop rows failing
  `tenant_id = 42`. If that tenant is 1% of the corpus, you return one result
  where ten were asked for, and sometimes zero.
- **Pre-filter by brute force** — select the tenant's rows first, then scan them
  exactly. Correct, but linear, and it abandons the index entirely.

What you want is filtered search the index itself understands: a partitioned or
per-tenant index, or an engine that evaluates the predicate during graph
traversal. Decide this before choosing a store — filtering support is where
engines differ most, and a hard multi-tenant isolation requirement usually means
one index per tenant regardless of engine.

### 6. Price the Re-Embedding Before Adopting the Model
Changing embedding models invalidates every stored vector. There is no migration
— there is a full re-encode of the corpus and a full index rebuild, and the two
models' vectors cannot be compared in between. Budget it as a recurring cost,
keep the source text and the chunk boundaries so you can re-encode without
re-ingesting, and stamp every row with the model and dimension that produced it.

## Warning Signs

- A dedicated vector database chosen before measuring `pgvector` on real data
- Recall never measured against exact search; index parameters set from a blog post
- Filtering applied after retrieval, with no check on how often results come back short
- Dense-only retrieval on a corpus full of identifiers, SKUs, or error codes
- Embeddings stored without the model name, version, and dimension alongside
- Chunk text discarded after embedding, making re-encoding a re-ingestion project
- Vectors in one system and their metadata in another, synchronised by hope
- Index build time not measured, discovered during the first production rebuild
- One shared index across tenants where isolation is a compliance requirement
