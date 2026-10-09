# RAG System Design (Minimal)

## Purpose
Answer questions over a corpus the model was never trained on, with citations — without the two standard outcomes: confident answers built from irrelevant chunks, and correct answers the system failed to retrieve.

## Core Techniques

### 1. Measure Retrieval Before You Touch the Prompt
Retrieval quality caps generation quality. If the answer is not in the retrieved set, no prompt wording recovers it — the model will either refuse or fabricate. Yet the reflex when a RAG system gives a bad answer is to rewrite the prompt.

Build a small labeled set — 50-200 questions, each mapped to the chunk ids that actually contain the answer — before tuning anything.

| Metric | Question it answers | Use it to |
|---|---|---|
| recall@k | Is the answer chunk anywhere in the top k? | Set k; diagnose chunking and embeddings |
| MRR / nDCG | How high up is it? | Decide whether reranking is needed |
| Precision@k | How much of the context is noise? | Tune k down; cut cost and distraction |

Diagnose in this order: recall@50 low → chunking or embedding problem. recall@50 high, recall@5 low → reranking problem. Both high, answer still bad → now it is a prompt problem. Most teams start at step three.

### 2. Chunk on Structure, Not on a Fixed Token Count
Fixed-size chunking cuts wherever the counter lands, which is frequently mid-table, mid-sentence, or between a heading and the paragraph it governs. The specific failure: an answer that straddles a boundary is in neither chunk in retrievable form, so recall for that question is zero regardless of k.

| Strategy | Good for | Breaks on |
|---|---|---|
| Fixed size + overlap | Homogeneous prose, a quick baseline | Tables, code, lists, anything structured |
| Recursive by separator (heading → paragraph → sentence) | Most documents | Documents with no structural markup |
| Document-structure aware (headings, sections, rows) | Manuals, policies, wikis, API docs | Scanned PDFs without layout recovery |
| Whole small document | FAQs, tickets, product records | Anything long |

Two habits fix most boundary losses: overlap adjacent chunks by 10-20% so a straddling fact appears whole in at least one, and prepend the document title and heading path to every chunk before embedding. "Refunds are processed within 5 days" is nearly unretrievable alone; "Acme Returns Policy > EU > Refunds: Refunds are processed within 5 days" is not.

Size to the embedding model's real context, and remember retrieval is only half the job — a huge chunk also crowds the generation window.

### 3. Retrieval and Reranking Are Two Stages With Opposite Goals
| | Stage 1: retrieve | Stage 2: rerank |
|---|---|---|
| Goal | Recall — do not lose the answer | Precision — put it first |
| Scope | Whole corpus | The 50-100 candidates |
| Method | Vector ANN + BM25 keyword, fused | Cross-encoder scoring query against each candidate |
| Cost | Milliseconds | Tens to hundreds of ms |
| Output | ~50 candidates | ~5 chunks |

Stage 1 must be cheap enough to run over everything and is judged only on whether the answer is in the candidate set. Stage 2 is expensive per document and only ever sees a shortlist. Retrieving five chunks straight from the vector index skips stage 2 and loses answers that ranked eleventh.

Run keyword search alongside vectors and fuse the results. Embeddings miss exact identifiers — error codes, part numbers, function names, rare proper nouns — precisely the terms users search for most confidently. Reciprocal rank fusion needs no score calibration:

```python
def rrf(rankings, k=60):
    scores = defaultdict(float)
    for ranking in rankings:                 # [vector_hits, bm25_hits]
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

### 4. Pick the Embedding Model on Your Own Corpus
Leaderboard scores are averaged over benchmarks that are not your data. Evaluate candidates on your labeled question set and compare recall@k directly.

What actually decides it: domain match (legal, medical, and code corpora behave very differently from general web text), the query-document asymmetry (short question against long passage — many models need the right prefix or instruction to handle this), the language mix, and dimension size, which sets index memory and query cost. Symmetric similarity models tuned for sentence-pair tasks routinely underperform on question-to-passage retrieval.

Treat the embedding model as a pinned dependency. Changing it invalidates every stored vector and requires a full re-index; plan for a dual-index migration rather than an in-place swap.

### 5. Ground the Answer and Make Citations Verifiable
```
Answer only from the sources below. Every claim must cite a source id.
If the sources do not contain the answer, say so and cite nothing.

<source id="c_418">…</source>
<source id="c_92">…</source>
```

Then verify the citation programmatically: every id the model emits must exist in what you actually sent. A cited id that was not in the context is a hallucinated citation, and it is trivially detectable — this single check catches the most damaging failure mode, an authoritative-looking answer with a fabricated reference.

Give the model an explicit way to say the sources are insufficient, and reward it — a refusal with no citation is a correct answer to an unanswerable question. Without that option the model will synthesize from the closest chunk it has.

### 6. Evaluate Retrieval and Generation Separately
| Stage | Measures | Tells you |
|---|---|---|
| Retrieval | recall@k, nDCG | Whether the answer was available at all |
| Generation | Faithfulness to the sources, citation validity, answer correctness | Whether the model used what it was given |

A single end-to-end "is the answer good" score cannot distinguish "we never retrieved it" from "we retrieved it and the model ignored it", and those need opposite fixes. Track them apart, and keep every production failure as a permanent case in the eval set.

## Warning Signs

- No labeled question-to-chunk set, so retrieval quality is unmeasured
- Fixed-size chunking with no overlap and no structural awareness
- Chunks embedded without their document title or heading path
- Vector search only, with no keyword channel for identifiers and codes
- Top-k straight from the vector index with no reranking stage
- k tuned by feel, never against recall@k
- Citations displayed but never validated against the ids actually sent
- No refusal path, so an empty retrieval still produces a confident answer
- End-to-end quality scored as one number, hiding which stage failed
- Embedding model swapped without a re-index plan
- Chunks retrieved without permission filtering applied at query time
