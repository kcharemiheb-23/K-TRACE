# Phase 10U - Retrieval Upgrade and Baseline-vs-Upgraded Comparison

## Goal
Upgrade the dense semantic retriever using corpus enrichment, hybrid BM25 plus dense retrieval with score fusion, and metadata-aware reranking, then compare upgraded retrieval against the Phase 10R baseline using the same SMART metrics, queries, and ground truth.

## Motivation
Phase 10R demonstrated that the dense semantic retriever produces acceptable MRR at 0.73 but weak Precision@5 at 0.52 and Recall@5 at 0.17, with cross-class contamination of 0.42. Root-cause analysis identified that case documents in the Phase 10A corpus differ in only four lines per template, which prevents semantic embeddings from discriminating between attack families. Phase 10U addresses this with four upgrade levers applied in sequence.

## Upgrade levers
- Part A: corpus enrichment using Phase 7 run-level telemetry and family-specific evidence vocabulary
- Part B: parallel vectorstore rebuild with one chunk per case and full metadata (family, intensity, class_label, doc_type)
- Part C: hybrid BM25 plus dense retrieval with Reciprocal Rank Fusion plus metadata-aware reranking
- Part D: comparative SMART evaluation against Phase 10R baseline with bootstrap confidence intervals, per-family decomposition, and ablation study

## Outputs
- artifacts/phase10U/corpus_v2 enriched corpus
- artifacts/phase10U/vectorstore_v2 parallel Chroma collection ids_rag_corpus_v2
- artifacts/phase10U/output upgrade-side ranked results and SMART metrics
- artifacts/phase10U/reports comparison report and per-part documentation
- artifacts/phase10U/dashboard data for the new dashboard

## Safety constraints
- Phase 10A baseline corpus must remain untouched
- Phase 10B baseline Chroma collection must remain untouched
- Phase 10R baseline metrics must remain reproducible for comparison
- New work uses only parallel directories and a parallel collection name

## Reproducibility
All Phase 10U code lives under scripts/phase10U with a strict numerical ordering matching the four parts. Every part has a validation gate before the next part begins.
