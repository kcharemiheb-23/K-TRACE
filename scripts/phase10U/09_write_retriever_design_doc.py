#!/usr/bin/env python3
"""Phase 10U Part C - Write the upgraded retriever design document."""
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
OUT = ROOT / "artifacts" / "phase10U" / "reports" / "upgraded_retriever_design.md"


DOC = """# Phase 10U Upgraded Retriever - Design Document

## 1. Purpose

This document defines the formal design of the upgraded retriever introduced in
Phase 10U, including its retrieval modes, scoring formulas, parameter choices,
and the relationship to the Phase 10R baseline. It is intended as the canonical
reference for the supervisor demo, the academic report, and the dashboard
methodology page.

## 2. Why an upgrade was required

The Phase 10R retriever evaluation showed that the dense semantic retriever
produced acceptable Mean Reciprocal Rank but weak Precision@5, weak Recall@5,
and high cross-class contamination. Diagnostic analysis traced the root cause
to two issues. First, Phase 10A case documents differed in only four lines
between attack families because they shared an extensive boilerplate template,
which prevented sentence-level embeddings from discriminating between
families. Second, the retrieval pipeline used dense semantic similarity alone,
with no lexical signal for run identifiers and family-specific tokens.

Phase 10U addresses these issues with a layered upgrade. Part A enriched the
corpus with run-level telemetry and family-specific evidence vocabulary.
Part B built a parallel Chroma collection with full chunk metadata and a
parallel BM25 index over the same chunks. Part C, documented here, defines
the upgraded retriever module that combines these components.

## 3. Retrieval modes

The upgraded retriever exposes four modes through a single function signature.

### 3.1 dense_only

Pure semantic vector retrieval against the Chroma collection
`ids_rag_corpus_v2`. The query is embedded with the same MiniLM model used in
Phase 10B, then the top-k chunks are returned by cosine similarity. This mode
is included to isolate the effect of corpus enrichment, because it differs
from the Phase 10R baseline only in the corpus content, not in the algorithm.

### 3.2 bm25_only

Pure sparse lexical retrieval using the standard Okapi BM25 formulation
implemented in `rank_bm25.BM25Okapi`. Tokenization is lowercase alphanumeric
splitting. This mode is included to isolate the effect of lexical sensitivity
to family-specific tokens and run identifiers.

### 3.3 rrf

Reciprocal Rank Fusion of the dense and BM25 rankings. The fused score for
chunk `d` is:
RRF_score(d) = sum over rankers r of 1 / (k + rank_r(d))
where `rank_r(d)` is the position of chunk `d` in ranker `r`'s ordered list
(1-indexed) and `k` is the standard rank-fusion constant. We use `k = 60`
following Cormack, Clarke, and Buettcher (SIGIR 2009), which is the default
adopted across the IR research community. Each ranker returns a candidate
pool of 30 chunks, of which the fused top-k are selected.

The crucial property of RRF is that it operates on ranks rather than raw
scores, which removes the need to calibrate dense cosine similarities against
BM25 term-frequency scores. The two scores live in incompatible numeric
ranges and cannot be averaged directly; RRF sidesteps this entirely.

### 3.4 rrf_plus_metadata_rerank

Reciprocal Rank Fusion as in mode 3.3, followed by a soft metadata boost
applied to chunks whose `family` metadata matches the predicted family for
the current query. The boost is:
boosted_score(d) = RRF_score(d) + b * 1 / (k + 1)    if family(d) == expected
= RRF_score(d)                       otherwise
with `b = 0.15`. The boost magnitude is intentionally on the same order as a
single-rank improvement in RRF, so it can break ties between equally-similar
chunks of different families but cannot promote a wholly irrelevant chunk
into the top-k. This is the lever that addresses the boilerplate-tail
near-duplicate failure mode identified in Phase 10R, where chunks at ranks
four through six had identical distances to ten decimal places and could not
be distinguished by similarity alone.

The `expected_family` parameter is supplied by the caller. In the Phase 10D
integrated pipeline, this is the family predicted by the multiclass ML model
for the current run, which makes retrieval prediction-aware and creates a
feedback loop between the classical detector and the LLM reasoning layer.

## 4. Parameter choices and justification

| Parameter | Value | Rationale |
|---|---|---|
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 | Same as Phase 10B, ensures fair comparison. |
| Chroma collection | ids_rag_corpus_v2 | Parallel to baseline; baseline preserved. |
| BM25 implementation | rank_bm25.BM25Okapi | Standard library, pure Python, no compiled deps. |
| BM25 tokenizer | lowercase alphanumeric split | Matches IR research convention. |
| RRF constant k | 60 | Cormack et al. SIGIR 2009 standard. |
| Metadata boost b | 0.15 | Tuned so boost magnitude equals roughly one rank position in RRF. |
| Candidate pool per ranker | 30 | Roughly 3x final top_k; supplies enough material for fusion. |

## 5. Schema compatibility with Phase 10R

The upgraded retriever writes ranked-results CSVs in the exact same column
schema as the Phase 10R baseline. This means the existing Phase 10R scoring
script `scripts/phase10R/05_score_retriever_smart_metrics.py` consumes the
upgraded outputs without modification. Part D will exploit this to run the
identical SMART metrics computation against all four upgrade modes plus the
baseline, producing a unified comparison table.

## 6. Relationship to the researcher and the embedding model

The researcher contribution in Phase 10U is the controlled design of:
- the enriched corpus content,
- the chunk metadata schema,
- the four-mode retrieval architecture,
- the Reciprocal Rank Fusion configuration,
- the metadata-aware boost calibration,
- the comparison protocol against the Phase 10R baseline.

The embedding model and the BM25 library are off-the-shelf components. The
research contribution is not the components but the controlled design and
evaluation of retrieval behavior in a cloud-native IDS reasoning pipeline.
"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(DOC, encoding="utf-8")
    print(f"WROTE: {OUT}")


if __name__ == "__main__":
    main()
