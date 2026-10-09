# Vector Store Selection (Verbose)

## Core Patterns

### Start From Postgres and Justify Leaving It

Most teams reach for a vector database at a scale where a Postgres extension
would have been simpler and faster to operate. The pitch for a dedicated store is
scale and speed; the cost is a second system of record for data that is mostly
metadata with a float array attached.

What staying relational keeps:

- **The join.** Retrieval is almost never "nearest neighbours" alone. It is
  nearest neighbours *belonging to this tenant, in this workspace, not archived,
  updated since March, with the document title and the author*. In SQL that is one
  statement. Across two systems it is a fetch, a second fetch, and reconciliation
  logic that will drift.
- **Transactions.** A document update and its embedding update commit together,
  or they do not commit. Split systems have a window where the index points at
  text that no longer exists.
- **Operations you already run.** Backup, restore, point-in-time recovery,
  replication, upgrades, an on-call runbook. A new datastore duplicates every one.

Rough capability, and the numbers matter more than the marketing:

| Corpus | pgvector + HNSW | Verdict |
|---|---|---|
| < 100k vectors | Single-digit ms, index builds in seconds | Exact search may be enough; index optional |
| 100k – 1M | 10–50 ms p95 on a modest instance | Comfortable. No reason to leave |
| 1M – 10M | Tens of ms if the index fits in RAM; build takes minutes to hours | Works, but index memory and rebuild time now need planning |
| 10M – 100M | Needs partitioning, a large instance, careful `maintenance_work_mem` | Evaluate dedicated stores seriously |
| > 100M | Sharding you build yourself | A purpose-built store is usually right |

```sql
CREATE TABLE chunk (
  id          bigserial PRIMARY KEY,
  doc_id      bigint NOT NULL REFERENCES document(id) ON DELETE CASCADE,
  tenant_id   bigint NOT NULL,
  ord         int    NOT NULL,
  body        text   NOT NULL,
  body_tsv    tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED,
  embedding   vector(768),
  embed_model text   NOT NULL,        -- which model produced this vector
  embed_ver   int    NOT NULL,        -- bump to invalidate
  UNIQUE (doc_id, ord)
);

CREATE INDEX chunk_vec_idx ON chunk USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
CREATE INDEX chunk_fts_idx ON chunk USING gin (body_tsv);
CREATE INDEX chunk_tenant_idx ON chunk (tenant_id);
```

Genuine reasons to move to a dedicated store:

| Reason | Signal |
|---|---|
| Corpus size | Tens of millions of vectors and growing; index no longer fits alongside the working set |
| Query load | Sustained vector QPS that would starve the OLTP workload sharing the instance |
| Rebuild cadence | Re-embedding often enough that index builds must not touch the transactional database |
| Filtering model | Need for filtered ANN across high-cardinality attributes the extension handles poorly |
| Operational preference | Team wants a managed service and accepts two systems of record |

"We might grow" is not a reason. Neither is a benchmark run on someone else's
corpus with someone else's filter distribution.

### Index Types and What They Trade

Every approximate index buys latency with recall. The three families differ in
*where* they spend the cost.

| Property | Flat (exact) | IVF (inverted file) | HNSW (graph) |
|---|---|---|---|
| Structure | None; scan all vectors | k-means centroids; vectors assigned to lists | Multi-layer proximity graph |
| Build | Instant | Train on a sample, then assign — minutes | Incremental insert, slowest of the three |
| Query | O(n) distance computations | Scan `nprobe` nearest lists | Greedy descent, `ef_search` candidates |
| Memory | Vectors only | Vectors + centroids (small) | Vectors + graph edges, roughly 1.5–2× |
| Recall | 100% by definition | 90–98% at sane `nprobe` | 95–99%+ at moderate `ef_search` |
| Inserts | Free | Degrade as the clustering ages | Handled natively |
| Deletes | Free | Free | Tombstoned; graph degrades, needs periodic rebuild |
| Tuning knob | — | `nlist` (build), `nprobe` (query) | `m`, `ef_construction` (build), `ef_search` (query) |

Practical guidance:

- **Flat is underrated.** At 100k vectors of 768 dimensions, exact search is a
  300 MB matrix multiply — a few milliseconds with a decent BLAS. It has perfect
  recall, zero build time, no parameters, and no rebuild problem. Use it until it
  is demonstrably too slow, and keep it forever as the ground truth you measure
  approximate indexes against.
- **IVF when memory is the binding constraint.** The graph overhead of HNSW is
  real; IVF's centroid table is negligible. IVF also builds far faster, which
  matters if you re-embed often. Its weakness is that the clustering is trained
  on a snapshot: a corpus that drifts in content needs retraining, and until it
  gets one, recall quietly falls.
- **HNSW when latency at high recall is the requirement.** It dominates the
  recall-latency frontier and absorbs inserts without retraining. Pay for it in
  memory and build time, and remember that deletes only tombstone — a corpus
  with heavy churn needs a scheduled rebuild or recall decays.
- **Quantization is an orthogonal axis.** Product quantization or scalar
  quantization compresses the vectors themselves and can be layered on either
  IVF or HNSW, trading a few points of recall for 4–32× memory reduction. Reach
  for it when memory, not algorithm, is what is breaking.

`nlist` for IVF is conventionally around `sqrt(n)`; `nprobe` then starts near 1%
of `nlist` and rises until recall clears target. For HNSW, `m = 16` and
`ef_construction = 64` are reasonable defaults, with `ef_search` the only knob you
should be turning at query time.

### Measure Recall Before Tuning Anything

An approximate index does not fail loudly. It returns plausible documents that
are not the nearest ones, retrieval quality sags, and the team blames the prompt.

```python
import numpy as np

def exact_topk(corpus: np.ndarray, queries: np.ndarray, k: int) -> np.ndarray:
    """Ground truth. Normalize first so dot product is cosine."""
    c = corpus / np.linalg.norm(corpus, axis=1, keepdims=True)
    q = queries / np.linalg.norm(queries, axis=1, keepdims=True)
    sims = q @ c.T
    return np.argpartition(-sims, k, axis=1)[:, :k]

def recall_at_k(index, queries, truth, k: int) -> float:
    hits = sum(len(set(index.search(q, k)) & set(t[:k]))
               for q, t in zip(queries, truth))
    return hits / (k * len(queries))
```

Sweep the query-time knob and record both axes:

| `ef_search` | recall@10 | p95 latency |
|---|---|---|
| 20 | 0.87 | 3 ms |
| 40 | 0.94 | 5 ms |
| 80 | 0.975 | 9 ms |
| 200 | 0.993 | 22 ms |

Pick the smallest value clearing the target. Note what this table also tells you:
if your product is fine at recall 0.94, you are paying 4× latency for the last
five points. That decision should be made against a retrieval quality metric on
real queries (see `llm-evaluation-and-testing`), not against the recall number in
isolation — recall@10 against exact search measures fidelity to the embedding
model, not usefulness to the user.

Use a held-out sample of *real* queries. Synthetic or random-vector queries have
different neighbourhood density and will report recall you do not have.

### Hybrid Retrieval: Lexical and Dense Together

Dense embeddings encode meaning and lose literals. The failures are consistent
and easy to reproduce:

| Query | Dense-only behaviour |
|---|---|
| `ERR_CONN_RESET_7741` | Returns semantically similar error discussions, not that code |
| `part MX-4471-B` | Returns other part numbers of similar shape |
| "invoices *not* paid" | Negation is weakly encoded; paid invoices rank highly |
| A rare surname | Not in the model's effective vocabulary; near-random |

BM25 handles all four and fails at paraphrase, which is exactly what dense
retrieval is good at. The two are complementary, so run both.

**Fusion by reciprocal rank** is the default because it needs no calibration:

```python
from collections import defaultdict

def rrf(rankings: list[list[str]], k: int = 60, weights=None) -> list[str]:
    weights = weights or [1.0] * len(rankings)
    scores = defaultdict(float)
    for ranked, w in zip(rankings, weights):
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] += w / (k + rank)
    return sorted(scores, key=scores.__getitem__, reverse=True)
```

Cosine similarity lives in roughly [0, 1] with a compressed useful range; BM25 is
unbounded and corpus-dependent. A weighted sum of the two requires normalization
that has to be re-derived whenever the corpus changes. RRF uses only ordering, so
it does not.

**Reranking is the third stage and usually the largest single quality gain.**
Retrieve 50–100 candidates cheaply with hybrid search, then score each against
the query with a cross-encoder and keep the top 5–10. The cross-encoder sees the
query and document together rather than comparing two independently-computed
vectors, which is why it is both far more accurate and far too slow to run over
the whole corpus.

```
query → [BM25 top-50] ┐
                      ├→ RRF → top-50 → cross-encoder rerank → top-8 → context
query → [ANN top-50]  ┘
```

### Filtering: the Pre- vs Post-Filter Trap

Almost every real query is constrained: this tenant, this workspace, not deleted,
within a date range. How the engine applies that predicate determines whether
your results are correct.

| Strategy | Mechanism | Failure mode |
|---|---|---|
| Post-filter | ANN returns top-k, predicate removes non-matching | Returns fewer than k, sometimes zero, when the filter is selective |
| Naive pre-filter | Predicate selects a subset, then exact scan | Correct but linear; index unused; slow on large subsets |
| Filtered ANN | Predicate evaluated during traversal | Correct and fast, but engine support varies widely |
| Partitioned index | One index per filter value | Correct and fast; only viable for low-cardinality partitions |

The post-filter failure is the one that ships. With `tenant_id` matching 1% of
the corpus and `k = 10`, retrieving top-100 and filtering leaves about one
result. The endpoint returns 200 OK with a single document, the answer is thin,
and nothing in the logs says "recall collapsed".

Three workable approaches:

1. **Partition by the dominant filter.** If every query filters on `tenant_id`,
   build one index per tenant. Small indexes, exact isolation, no filtered-ANN
   support required. The cost is index proliferation and a poor fit for tenants
   with a handful of documents.
2. **Use an engine with true filtered traversal**, and verify it on your filter
   selectivity — not the vendor's. Measure recall with the predicate applied, at
   the selectivity your production queries have.
3. **Switch strategy by selectivity.** If the predicate matches few enough rows,
   scan them exactly; otherwise use the index and post-filter with a generous
   over-fetch.

```python
def search(query_vec, predicate, k=10):
    n = count_matching(predicate)
    if n <= 50_000:                      # cheap enough to scan exactly
        return exact_scan(query_vec, predicate, k)
    over = max(k * 10, k * ceil(total_rows / max(n, 1)))
    cand = ann_search(query_vec, k=min(over, 2000))
    return [c for c in cand if predicate(c)][:k]
```

Whatever you pick, **alert on short result sets**. `returned < k` on a query that
should have had matches is the signal that filtering is eating your results, and
it is otherwise invisible.

Hard multi-tenant isolation changes the calculus entirely: if a cross-tenant leak
is a compliance incident rather than a bug, use physically separate indexes and
do not rely on a predicate being applied correctly inside a shared graph.

### Re-Embedding and Index Rebuild Cost

Vectors from different models are not comparable. Not "less accurate" —
meaningless. So a model change is a full re-encode plus a full index build, and
during it the corpus is split across two incompatible spaces.

What it costs, at a million chunks:

| Stage | Driver | Order of magnitude |
|---|---|---|
| Re-encode | Embedding throughput, batch size, rate limits | Hours; the dominant money cost |
| Index build | HNSW is slow; IVF needs training then assignment | Minutes to hours |
| Validation | Retrieval quality on a query set, old vs new | Hours of wall clock, mostly waiting |
| Cutover | Dual-write or alias swap | Minutes, if planned |

The design decisions that make this survivable, all of which must be made before
the first ingestion:

- **Keep the source text and chunk boundaries.** If chunks are only reconstructible
  by re-crawling the source, re-embedding becomes re-ingestion, which is an order
  of magnitude more work and may not be possible at all for sources that changed.
- **Stamp every vector with model and version.** Without `embed_model` on the row
  you cannot tell which vectors are stale, and a partially migrated corpus is
  silently broken.
- **Build the new index beside the old one and swap by alias.** Never mutate in
  place; you lose the ability to roll back, and quality regressions from an
  embedding change are common enough to plan for.
- **Version chunking separately from embedding.** Changing chunk size or overlap
  also invalidates everything, and teams often discover this only after treating
  chunking as a tunable.
- **Re-rank the decision.** A newer embedding model is not automatically better on
  your corpus. Measure retrieval quality on your own query set before committing
  to a migration that costs a day of compute.

For steady-state operation, decide how updates reach the index: incremental upsert
(HNSW handles it; IVF's clustering ages), or periodic full rebuild (simple,
predictable, and fine if your corpus updates daily rather than continuously).
Deletes deserve explicit thought — tombstones accumulate, and a corpus with high
churn needs a scheduled compaction whether or not the engine advertises one.

## Common Anti-Patterns

❌ **Adopting a dedicated vector database before measuring the relational option
on real data.** Two systems of record, a synchronisation problem, and a new
on-call surface — bought at a scale where one index would have done.
✅ Benchmark `pgvector` (or equivalent) on your corpus and filters. Leave when a
measured number says to.

❌ **Setting index parameters from a blog post and never measuring recall.**
✅ Build an exact-search ground truth on a sample; sweep the query knob; pick the
smallest value that clears the target.

❌ **Post-filtering after ANN with no over-fetch and no monitoring.** Selective
filters return one result where ten were requested, silently.
✅ Filtered traversal, partitioned indexes, or selectivity-aware over-fetch —
plus an alert on short result sets.

❌ **Benchmarking recall without the production filter applied.** Unfiltered
recall of 0.98 says nothing about recall at 1% selectivity.
✅ Measure with real predicates at real selectivity.

❌ **Dense-only retrieval on a corpus full of identifiers, codes, and names.**
✅ Hybrid: BM25 plus dense, fused by reciprocal rank.

❌ **Fusing scores by weighted sum of cosine and BM25.** The scales are
incomparable and the weights need re-derivation whenever the corpus shifts.
✅ RRF, which uses only rank.

❌ **Skipping the reranker.** The largest available quality gain, left on the
table while the team tunes `ef_search`.
✅ Over-retrieve cheaply, rerank with a cross-encoder, pass a small context.

❌ **Storing vectors without the model, version, and dimension that produced
them.** Stale vectors become undetectable and the corpus mixes spaces.
✅ Stamp every row; make version a query predicate during migration.

❌ **Discarding chunk text after embedding.** Re-embedding turns into
re-ingestion from sources that may have changed underneath you.
✅ Keep the text and the chunk boundaries; re-encode from them.

❌ **Rebuilding an index in place during a model migration.** No rollback, and
mixed spaces while it runs.
✅ Build alongside, validate on a query set, swap by alias.

❌ **Treating chunk size as a free tunable.** Changing it invalidates every
vector exactly as a model change does.
✅ Version chunking; price a change the same way you price re-embedding.

❌ **One shared index where tenant isolation is a compliance requirement.**
✅ Physically separate indexes; do not stake an audit finding on a predicate.

❌ **Ignoring delete behaviour.** Tombstones accumulate, recall decays, nobody
notices because no metric tracks it.
✅ Scheduled compaction or rebuild, with recall measured before and after.

## Vector Store Selection Checklist

- [ ] Corpus size, growth rate, and query rate measured rather than estimated
- [ ] Relational extension benchmarked on real data before a dedicated store is chosen
- [ ] Embedding dimension fixed, and index memory at target scale calculated
- [ ] Index family chosen against an explicit recall target and memory budget
- [ ] Exact-search ground truth built on a held-out sample of real queries
- [ ] Recall@k measured, with the production filter applied at real selectivity
- [ ] Query-time knob (`ef_search` / `nprobe`) swept, smallest passing value chosen
- [ ] Filter strategy decided explicitly: partitioned, filtered-ANN, or over-fetch
- [ ] Alert on result sets shorter than k
- [ ] Multi-tenant isolation enforced physically where it is a compliance requirement
- [ ] Lexical retrieval available alongside dense, fused by rank not score
- [ ] Reranking stage evaluated against retrieval quality, not just latency
- [ ] Every vector stamped with model, model version, and chunking version
- [ ] Source text and chunk boundaries retained for re-encoding
- [ ] Index build time measured at full corpus size, not on a sample
- [ ] Re-embedding runbook written: build beside, validate, alias swap, roll back
- [ ] Delete and update path defined; compaction scheduled where tombstones accumulate
- [ ] Backup and restore of the index tested, or its rebuild-from-source time known
