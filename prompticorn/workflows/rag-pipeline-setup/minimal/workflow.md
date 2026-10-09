---
name: "rag-pipeline-setup"
description: "Build a retrieval-augmented pipeline and measure retrieval separately from generation"
agent: "mlai"
category: "ml"
related_workflows:
  - llm-feature-build
  - eval-harness-setup
  - prompt-iteration-cycle
---

# RAG Pipeline Setup Workflow

**Problem:** Ground an LLM feature in your own corpus, and be able to say whether a bad answer was a retrieval failure or a generation failure.

That distinction is the whole workflow. Teams that measure only end-to-end answer quality spend weeks rewriting prompts to fix a problem that was in the chunker.

## Steps

### 1. Inventory the Corpus Before Choosing Anything Else
The corpus determines the chunker, the index, and the access model. Answer these first:

| Question | If... | Consequence |
|---|---|---|
| How big? | < ~5k chunks | A brute-force or in-process index is enough; skip the vector DB |
| How structured? | Tables, code, forms | Naive text chunking will destroy it — chunk structurally |
| How fresh? | Changes hourly | You need incremental upsert and delete, not a nightly rebuild |
| Who may read what? | Mixed permissions | Permissions filter at query time, in the index — never post-hoc |
| Any duplicates? | Usually yes | Near-duplicates crowd out the top-k with the same answer |

Access control is the item that is expensive to retrofit. Store `allowed_principals` on every chunk from day one.

### 2. Chunk on Structure, Not on a Character Count
Split at headings, sections, function boundaries, or rows first, and only fall back to a size limit inside an oversized unit. Keep a small overlap (roughly 10–15%) so a sentence spanning a boundary survives.

Carry a header with each chunk — document title, section path, date, source URL. It improves both embedding quality and the model's ability to cite.

```
[Billing Guide > Refunds > Partial refunds | updated 2026-04-02]
Partial refunds may be issued within 90 days of purchase...
```

### 3. Embed and Index, Recording the Model Version
Embed chunk text including the header. Store the embedding model id and dimension in metadata: changing the embedding model invalidates the entire index, and a mixed-model index silently returns nonsense.

Enable hybrid search — dense vectors plus BM25 — unless you have measured that you do not need it. Dense retrieval alone misses exact identifiers, error codes, part numbers, and rare proper nouns, which is exactly what people search for.

### 4. Evaluate Retrieval on Its Own, Before Generation
Build 50–100 queries with the chunk ids that should be retrieved, then measure without any LLM in the loop.

| Metric | Reads on |
|---|---|
| Recall@k | Is the answer even in the context? The ceiling on everything downstream |
| MRR / nDCG | Is it near the top, where the model will actually use it? |
| Miss rate by tag | Which query types fail — acronyms, dates, multi-hop |

If recall@10 is 0.6, your maximum achievable answer quality is 0.6, and no prompt work changes that.

### 5. Rerank When Recall Is Good and Precision Is Not
Retrieve wide (k=30–50) with a cheap retriever, then rerank to 5–8 with a cross-encoder or a model-based reranker. This is the highest-leverage single addition to most RAG systems.

It fixes precision, not recall — if the right chunk is not in the wide set, reranking cannot invent it. Check recall@50 before reaching for it.

### 6. Ground the Generation Step Explicitly
Pass chunks as tagged, untrusted data with stable ids, require citations, and give the model an explicit way to say the context does not contain the answer.

```
<context>
<doc id="c_4471" source="Billing Guide > Refunds">Partial refunds may be issued within 90 days...</doc>
</context>
Answer only from <context>. Cite every claim as [doc id]. If the context does
not contain the answer, say so and stop.
```

Retrieved content is untrusted input — a chunk can carry an injected instruction. See the LLM safety and guardrails skill.

### 7. Measure End to End, With the Two Halves Separable
Score answers against your eval set, and for every failure record whether the correct chunk was retrieved. That single field splits your backlog into two very different queues: retrieval work and prompt work.

| Retrieved? | Answer correct? | Fix |
|---|---|---|
| No | No | Chunking, embeddings, hybrid, query rewriting |
| Yes | No | Prompt, context ordering, model |
| Yes | Yes, but uncited or hedged | Grounding instructions, citation format |

## Common Pitfalls

- Fixed-size chunking that cuts tables and code in half
- Dense-only retrieval on a corpus full of identifiers and error codes
- No retrieval metrics — only end-to-end answer quality
- Embedding model swapped without reindexing
- Permissions applied after retrieval instead of as an index filter
- Reranking added while recall is the actual bottleneck
- Near-duplicate documents filling the top-k
- Retrieved text concatenated into the prompt as if it were trusted
