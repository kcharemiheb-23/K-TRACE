# Phase 10U Part B - Vectorstore v2 and BM25 Index Report

## What this part did
Phase 10U Part B built a parallel Chroma vector collection ids_rag_corpus_v2 from the enriched corpus produced in Part A, and a parallel BM25 index over the same chunks. The Phase 10B baseline collection was not modified.

## Why
The Phase 10B baseline used the same MiniLM embedder but indexed Phase 10A boilerplate-heavy case documents and stored only minimal metadata. The v2 indexes use the enriched corpus, store structured family and intensity metadata, and add a sparse lexical index that complements the dense retriever in Part C.

## Index parameters
- Embedding model: sentence-transformers/all-MiniLM-L6-v2 (same as Phase 10B for fair comparison)
- Chroma persistent path: artifacts/phase10U/vectorstore_v2
- Collection name: ids_rag_corpus_v2
- Chunking for cases: one chunk per case (eliminates boilerplate-tail near-duplicates)
- Chunking for non-case docs: 900 chars with 120-char overlap (matches Phase 10B parameters)
- BM25 library: rank_bm25.BM25Okapi
- BM25 tokenizer: lowercase alphanumeric split

## Chunk statistics
- Total chunks: 43
- Median chunk size: 2490 chars
- By section: {'cases': 24, 'methodology': 6, 'ml_results': 6, 'features': 1, 'glossary': 6}
- By family: {'A1': 3, 'A2': 3, 'A3': 3, 'A4': 3, 'BENIGN': 12, 'UNKNOWN': 19}
- By doc_type: {'case': 24, 'methodology': 6, 'ml_results': 6, 'features': 1, 'glossary': 6}

## Metadata schema for every chunk
- chunk_id
- doc_name
- doc_stem
- section
- source_path
- family (A1, A2, A3, A4, BENIGN, UNKNOWN)
- class_label
- intensity (low, medium, high, none)
- run_id (for case chunks)
- doc_type (case, methodology, ml_results, features, glossary)
- chunk_index

## BM25 provenance
{
  "built_at_utc": "2026-04-28T09:32:27.183279+00:00",
  "chunk_count": 43,
  "tokenizer": "lowercase_alnum_split",
  "library": "rank_bm25.BM25Okapi",
  "chunks_source": "./artifacts/phase10U/chunks/chunk_records_v2.jsonl"
}

## Comparison vs Phase 10B baseline
- Phase 10B chunk count: 62
- Phase 10U chunk count: 43
- Phase 10B case chunks: 48 (two per case via boilerplate-tail duplication)
- Phase 10U case chunks: 24 (one per case, no duplication)
- Phase 10B metadata keys per chunk: 4 (section, doc_name, source_path, doc_stem)
- Phase 10U metadata keys per chunk: 11 (adds family, class_label, intensity, run_id, doc_type, chunk_index, plus carries forward the 4 from Phase 10B)
- Phase 10B BM25 index: none
- Phase 10U BM25 index: rank_bm25.BM25Okapi over 43 chunks

## Safety check
The Phase 10B baseline collection at artifacts/phase10B/vectorstore was not touched during Part B. This was verified by md5sum comparison of chroma.sqlite3 before and after Part B.

## Next step
Phase 10U Part C will implement the upgraded retriever using these two indexes, with Reciprocal Rank Fusion plus metadata-aware reranking, and produce ranked results that the existing Phase 10R scoring pipeline can consume directly.
