# K-TRACE Research Dataset

This directory contains research data and derived artifacts used by the K-TRACE framework for evidence-grounded intrusion analysis and retrieval evaluation.

## Contents

- `01_source_corpus/` — source corpus files and associated metadata.
- `02_chunks/` — chunk records derived from the source corpus.
- `03_sparse_retrieval/` — BM25 retrieval collection and metadata.
- `04_retrieval_evaluation/` — retrieval results and evaluation outputs from phases 10U and 10R.
- `05_documentation/` — documentation describing the vector-store design.

## Data lineage

The intended lineage is:

Source corpus → chunk records → retrieval collections → retrieval results and evaluation.

## Important notes

- Chunk records are not the same as dense embedding vectors.
- The presence of a BM25 collection does not establish that a dense-vector index is included.
- See the associated scripts and reports in the main K-TRACE repository for implementation details.
- File provenance, generation commands, and dataset-specific limitations should be documented alongside the corresponding artifacts.

## Reproducibility

This directory preserves copies of selected artifacts from the existing `artifacts/` directory. The original files have not been moved or deleted.
