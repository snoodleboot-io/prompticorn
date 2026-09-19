# RAG System Design (Verbose)

## Core Patterns

### Retrieval Quality Caps Generation Quality

The generator can only work with what it is handed. If the passage containing
the answer is not in the retrieved set, no amount of prompt engineering
retrieves it — the model either declines or fabricates something plausible from
the nearest chunk it does have. The ceiling on end-to-end accuracy is recall.

This is worth stating plainly because the debugging reflex runs the other way.
A RAG system gives a wrong answer, and the team rewrites the prompt, adds "be
accurate", increases the temperature penalty, tries a larger model. None of it
moves a number that was set two stages earlier.

Build the measurement before the tuning. A labeled set of 50–200 real questions,
each annotated with the chunk ids that genuinely contain the answer, is enough
to make every subsequent decision empirical.

```jsonl
{"q": "How long do EU refunds take?", "relevant": ["policy_eu#refunds"]}
{"q": "What does error 4021 mean?",    "relevant": ["errcodes#4021"]}
{"q": "Can I expense a taxi?",          "relevant": ["travel#ground", "travel#limits"]}
```

| Observation | Diagnosis | Where to work |
|---|---|---|
| recall@50 low | The answer chunk is not findable at all | Chunking, embeddings, the keyword channel, or the corpus is missing it |
| recall@50 high, recall@5 low | It is findable but ranked badly | Add or tune reranking; check hybrid fusion |
| recall@5 high, answers still wrong | The context was right and unused or misused | Now, and only now, the prompt and grounding |
| recall high, precision@5 low | Too much noise alongside the answer | Lower k, tighten chunk size, stronger reranker |

Run this diagnosis in order. Skipping to the last row is the default behavior
and the reason RAG projects stall.

### Chunking: Where Answers Get Lost

Chunking is the highest-leverage decision in the pipeline and the one most often
made by accepting a default. A chunk is simultaneously the unit of embedding
(and therefore of semantic representation), the unit of retrieval, the unit of
citation, and a consumer of the generation window. Those four roles want
different sizes.

**The fixed-size failure, concretely.** Split at 512 tokens with no overlap and
a policy document breaks mid-section. The question "how long do EU refunds
take?" needs both the qualifier ("For orders shipped within the EU…") and the
duration ("…processed within 5 business days"), which now sit in different
chunks. Chunk A embeds as a statement about EU shipping; chunk B embeds as a
generic sentence about processing time. Neither is a strong match for the
question. Recall for that question is zero at any k, and it will remain zero
through every prompt revision.

| Strategy | Mechanism | Best for | Fails on |
|---|---|---|---|
| Fixed size, no overlap | Split every N tokens | A baseline to beat | Everything structured; boundary-straddling answers |
| Fixed size + 10–20% overlap | Sliding window | Homogeneous prose | Tables, code, long procedures |
| Recursive separators | Split on heading, then paragraph, then sentence, until under size | Most text corpora | Documents with no markup |
| Structure-aware | Respect headings, sections, list and table boundaries | Manuals, policies, wikis, API references | Scanned PDFs without layout recovery |
| Semantic | Split where embedding similarity between consecutive sentences drops | Unstructured narrative | Cost; unpredictable sizes |
| Whole document | One chunk per record | FAQs, tickets, product entries, short notes | Long documents |
| Parent–child | Embed small children, return the parent section | Precision of retrieval with context for generation | More index and plumbing complexity |

**Contextualize every chunk before embedding.** This is the cheapest large win
available. A bare chunk loses everything the document structure implied.

```python
def chunk_text(doc, section, chunk):
    return (f"{doc.title} > {' > '.join(section.heading_path)}\n"
            f"{chunk.text}")
# "Acme Returns Policy > EU Orders > Refunds
#  Refunds are processed within 5 business days of receipt."
```

Embed the contextualized form; store the raw text and its metadata for
citation. Pronouns and implicit subjects are what break isolated chunks — "It
must be returned within 30 days" is unretrievable when "it" was named two
headings up.

**Parent–child retrieval** resolves the size conflict directly: embed and
retrieve small precise children, then hand the generator the enclosing parent
section so the surrounding context comes along.

| | Small chunks (~200 tok) | Large chunks (~1500 tok) | Parent–child |
|---|---|---|---|
| Embedding precision | High | Diluted across topics | High |
| Context for the generator | Thin | Rich | Rich |
| Window cost at k=5 | Low | High | Medium |
| Citation granularity | Precise | Vague | Precise |
| Complexity | Low | Low | Medium |

**Tables, code, and lists need their own handling.** A table split across chunks
loses its header row, so the numbers are unlabeled and the model will guess at
column meaning. Keep tables whole where possible, and repeat the header if a
long table must be split. Code should split on function or class boundaries,
never on line count.

Overlap is insurance, not a strategy: 10–20% covers the straddling-fact case
cheaply, but it inflates the index and creates near-duplicate retrievals, so
deduplicate overlapping hits before assembling context.

### Embedding Choice

The decision is empirical and corpus-specific. Public leaderboard averages are
computed over benchmark mixes that do not resemble your data, and the ranking
frequently inverts on a specialized corpus.

| Factor | Why it decides the outcome |
|---|---|
| Domain match | Legal, clinical, and code text have vocabulary and structure general-web models represent poorly |
| Asymmetric retrieval | Short query against long passage is a different task from sentence similarity; models tuned for the latter underperform, and many require a query/document prefix or instruction to work correctly |
| Language coverage | A multilingual corpus with a monolingual model silently fails on part of the traffic |
| Dimension count | Sets index memory, query latency, and cost; higher is not automatically better on a small corpus |
| Max sequence length | Caps usable chunk size; silent truncation past it is common and invisible |
| Hosted vs self-hosted | Latency, per-token cost, data residency, and whether a provider deprecation forces a re-index on their schedule |

```python
for name, embedder in candidates.items():
    index = build_index(chunks, embedder)
    r5, r50 = evaluate(index, labeled_questions, ks=(5, 50))
    print(f"{name}: recall@5={r5:.3f} recall@50={r50:.3f} dim={embedder.dim}")
```

Two operational rules. Use the same model and the same prefix convention for
indexing and querying — an asymmetric model queried without its query prefix
degrades quietly rather than erroring. And treat the embedding model as a pinned
dependency with a migration plan: changing it invalidates every stored vector.
Re-index into a second index, compare recall on the labeled set, cut over, then
retire the old one. In-place swaps produce a corpus where old and new vectors
are not comparable, and the symptom is retrieval that gets mysteriously worse
for a subset of documents.

### Retrieval and Reranking Are Two Stages

They optimize opposite quantities and should be designed as separate components.

| | Stage 1 — retrieve | Stage 2 — rerank |
|---|---|---|
| Objective | Recall: the answer must be in the candidate set | Precision: the answer must be at the top |
| Scope | The entire corpus | 50–100 candidates |
| Model | Bi-encoder ANN + BM25, fused | Cross-encoder scoring the query jointly with each candidate |
| Why it scales | Documents embedded once, offline | Never runs over the corpus |
| Latency | Single-digit to tens of ms | Tens to low hundreds of ms |
| Typical output | 50 candidates | 3–8 chunks |

A bi-encoder embeds query and document independently, so the comparison is a
dot product and can be indexed — that is what makes corpus-scale search
possible, and also what limits its accuracy, because the document's embedding
was computed without knowledge of the query. A cross-encoder reads both together
and is substantially more accurate at ordering, at a cost that forbids running it
over anything but a shortlist.

Taking top-5 straight from the vector index is the common shortcut, and it
discards every answer that ranked eleventh — which, on the labeled set, is
usually a visible fraction of the questions.

**Hybrid retrieval.** Dense vectors capture meaning and miss exact tokens.
Keyword search (BM25) does the reverse. The terms users are most confident
about — `ERR_4021`, `SKU-88231`, `parse_header()`, an unusual surname — are
exactly the ones embeddings blur.

```python
def hybrid(query, k_each=50):
    dense  = vector_index.search(embed(query), k=k_each)
    sparse = bm25_index.search(query, k=k_each)
    return rrf([d.ids for d in (dense, sparse)])

def rrf(rankings, k=60):
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

Reciprocal rank fusion combines rankings rather than scores, which avoids
calibrating a cosine similarity against a BM25 score — two quantities on
incomparable scales whose relative weighting nobody can tune defensibly.

**Filter before you search, not after.** Permissions, tenant, document status,
and recency belong in the index as metadata filters applied during the ANN
query. Post-filtering a top-50 list can leave three results, and permission
filtering applied after retrieval has a habit of becoming permission filtering
applied only sometimes. Retrieval that ignores access control is a data-leak
path with a natural-language interface.

**Query transformation** is worth considering once the basics are in place: in
multi-turn chat the query must be rewritten standalone ("what about the EU?"
retrieves nothing on its own), and for multi-part questions, decomposing into
sub-queries and retrieving for each raises recall. Both add a model call and
latency, so measure the recall gain before adopting them.

### Grounding and Citation

```
Use only the sources below. Every factual claim must carry the id of the source
that supports it. If the sources do not answer the question, say so explicitly
and cite nothing. Do not use knowledge outside the sources.

<source id="c_418" title="Acme Returns Policy > EU Orders">…</source>
<source id="c_92"  title="Shipping FAQ > Timelines">…</source>

Question: {{ question }}
```

Instructions alone are not enough; verify mechanically.

```python
def verify(answer, sent_ids):
    cited = set(re.findall(r"\[c_(\w+)\]", answer.text))
    ghosts = cited - sent_ids
    if ghosts:
        metrics.incr("rag.hallucinated_citation", len(ghosts))
        return Repair(reason=f"cited ids not in context: {sorted(ghosts)}")
    if not cited and not answer.declined:
        return Repair(reason="uncited claim")
    return Ok()
```

A citation id that was never in the context is a fabricated reference, and it is
detectable with a set difference. This check costs nothing and catches the most
damaging failure mode in the system: an authoritative answer with an official-
looking source attached that does not exist. Do it on every response.

Beyond id existence, faithfulness — whether the cited passage actually supports
the claim — needs either a lightweight entailment check or an LLM judge on a
sample. It is more expensive and worth running continuously on a traffic sample
rather than inline.

**The refusal path is a feature.** Give the model an explicit, rewarded way to
say the sources are insufficient, and surface it in the UI as a legitimate
outcome. Without it, a retrieval that returned nothing relevant still yields a
fluent answer assembled from the closest available chunk. Gate on retrieval
scores too: if the best reranker score is below a threshold calibrated on the
labeled set, decline before calling the generator at all — it is cheaper and
more honest.

Display citations as links to the source location, not as bare ids. A citation
the user cannot click is a claim of provenance, not evidence of it, and users
calibrate their trust on whether verification is possible.

### Evaluating the Two Stages Separately

| Layer | Metrics | Needs labels? | Cadence |
|---|---|---|---|
| Retrieval | recall@k, MRR, nDCG, precision@k | Question → relevant chunk ids | Every index or chunking change, in CI |
| Reranking | nDCG@5, recall@5 vs recall@50 gap | Same set | Every reranker change |
| Generation faithfulness | Citation validity, claim-level support rate | Partly automatable | Continuous on a sample |
| Answer correctness | Exact match, or graded against reference answers | Reference answers | Per release |
| End-to-end product | Deflection, thumbs-down rate, escalation rate | No | Continuous |

The reason to keep these apart is diagnostic. A single end-to-end score cannot
tell you whether the answer was never retrieved or was retrieved and ignored,
and those two have nothing in common as fixes. Teams that track only the
end-to-end number end up alternating between prompt changes and chunk-size
changes with no way to attribute improvement to either.

Two habits keep the eval honest: every production failure becomes a permanent
case in the labeled set, and the eval runs in CI on any change to chunking,
embeddings, retrieval, reranking, or the prompt — those five are not independent,
and a chunk-size change can degrade a prompt that was tuned around the old
context shape.

### Keeping the Index Current

An index that lags the corpus produces a distinctive failure: the system answers
correctly from a policy that was revoked last month, cites it, and the citation
looks perfect.

| Concern | Approach |
|---|---|
| Updates | Re-chunk and re-embed at document granularity; delete the old chunk ids in the same transaction as the insert |
| Deletions | Propagate immediately — a deleted document that still answers questions is a compliance problem |
| Staleness | Store `indexed_at` per chunk and alert on the age distribution, not the mean |
| Freshness in ranking | Include recency as a rerank feature where the corpus has versioned documents |
| Re-embedding | Dual-index migration with a recall comparison on the labeled set before cutover |
| Cost | Content-hash chunks so unchanged text is not re-embedded on every crawl |

## Common Anti-Patterns

❌ **Tuning the prompt to fix a retrieval failure.**
✅ Measure recall@k first; if the answer was not retrieved, the prompt is irrelevant.

❌ **No labeled question-to-chunk set.**
✅ 50–200 real questions with annotated relevant chunks, before any tuning.

❌ **Fixed-size chunking with no overlap and no structural awareness.**
✅ Split on document structure; 10–20% overlap; keep tables and functions intact.

❌ **Embedding bare chunk text.**
✅ Prepend title and heading path so the chunk is interpretable standing alone.

❌ **Vector search only.**
✅ Hybrid dense + BM25 fused with RRF, so identifiers and codes are still findable.

❌ **Top-k straight from the vector index.**
✅ Retrieve broad for recall, rerank with a cross-encoder for precision.

❌ **k chosen by intuition.**
✅ Chosen from the recall@k curve against precision and window cost.

❌ **Choosing an embedding model from a leaderboard.**
✅ Benchmark candidates on your corpus and your questions.

❌ **Swapping embedding models in place.**
✅ Dual-index migration with a recall comparison before cutover.

❌ **Permission filtering applied to results after retrieval.**
✅ Metadata filters inside the ANN query, so unauthorized chunks are never candidates.

❌ **Displaying citations without validating them.**
✅ Verify every cited id exists in the context actually sent; meter the violations.

❌ **No way for the system to say "not in the sources."**
✅ An explicit refusal path, plus a retrieval-score threshold that declines before generating.

❌ **One end-to-end quality score.**
✅ Retrieval and generation measured separately, because they fail for unrelated reasons.

❌ **An index that is only ever appended to.**
✅ Updates and deletes propagated transactionally; chunk age monitored.

## RAG Design Checklist

- [ ] Labeled question → relevant-chunk set exists and grows with every production failure
- [ ] recall@k, nDCG, and precision@k measured and tracked over time
- [ ] Chunking respects document structure; tables and code kept intact
- [ ] Overlap configured, and overlapping hits deduplicated before assembly
- [ ] Chunks contextualized with title and heading path before embedding
- [ ] Chunk size validated against both the embedder's max length and the generation budget
- [ ] Embedding model selected by benchmarking on this corpus
- [ ] Same model and prefix convention used for indexing and querying
- [ ] Re-embedding migration plan documented (dual index, recall comparison, cutover)
- [ ] Hybrid dense + keyword retrieval with rank fusion
- [ ] Cross-encoder reranking between retrieval and generation
- [ ] Permission, tenant, and status filters applied inside the retrieval query
- [ ] Multi-turn queries rewritten standalone before retrieval
- [ ] Grounding instruction restricting claims to the provided sources
- [ ] Citation ids validated against the ids actually sent; violations metered
- [ ] Explicit refusal path, plus a score threshold that declines before generating
- [ ] Citations rendered as links to the source location
- [ ] Faithfulness sampled continuously; retrieval and generation evaluated separately
- [ ] Eval suite runs in CI on any chunking, embedding, retrieval, rerank, or prompt change
- [ ] Index updates and deletes propagate; chunk age monitored and alerted
