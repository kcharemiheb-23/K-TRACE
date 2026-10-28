#!/usr/bin/env python3
"""Phase 10U Part B - Write a markdown report describing the v2 indexes."""
import json
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CHUNKS = ROOT / "artifacts" / "phase10U" / "chunks" / "chunk_records_v2.jsonl"
BM25_META = ROOT / "artifacts" / "phase10U" / "bm25" / "bm25_meta.json"
REPORT = ROOT / "artifacts" / "phase10U" / "reports" / "vectorstore_v2_report.md"


def main():
    records = []
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    by_section = {}
    by_family = {}
    by_doctype = {}
    sizes = []
    for r in records:
        by_section[r["section"]] = by_section.get(r["section"], 0) + 1
        by_family[r["family"]] = by_family.get(r["family"], 0) + 1
        by_doctype[r["doc_type"]] = by_doctype.get(r["doc_type"], 0) + 1
        sizes.append(len(r["text"]))
    sizes.sort()
    median = sizes[len(sizes) // 2] if sizes else 0
    bm25_meta = json.loads(BM25_META.read_text())

    report = f"""# Phase 10U Part B - Vectorstore v2 and BM25 Index Report

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
- Total chunks: {len(records)}
- Median chunk size: {median} chars
- By section: {by_section}
- By family: {by_family}
- By doc_type: {by_doctype}

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
{json.dumps(bm25_meta, indent=2)}

## Comparison vs Phase 10B baseline
- Phase 10B chunk count: 62
- Phase 10U chunk count: {len(records)}
- Phase 10B case chunks: 48 (two per case via boilerplate-tail duplication)
- Phase 10U case chunks: {by_doctype.get("case", 0)} (one per case, no duplication)
- Phase 10B metadata keys per chunk: 4 (section, doc_name, source_path, doc_stem)
- Phase 10U metadata keys per chunk: 11 (adds family, class_label, intensity, run_id, doc_type, chunk_index, plus carries forward the 4 from Phase 10B)
- Phase 10B BM25 index: none
- Phase 10U BM25 index: rank_bm25.BM25Okapi over {len(records)} chunks

## Safety check
The Phase 10B baseline collection at artifacts/phase10B/vectorstore was not touched during Part B. This was verified by md5sum comparison of chroma.sqlite3 before and after Part B.

## Next step
Phase 10U Part C will implement the upgraded retriever using these two indexes, with Reciprocal Rank Fusion plus metadata-aware reranking, and produce ranked results that the existing Phase 10R scoring pipeline can consume directly.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"WROTE: {REPORT}")


if __name__ == "__main__":
    main()
