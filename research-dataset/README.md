# K-TRACE Research Dataset

This directory contains the datasets, experimental evidence, retrieval artifacts, and evaluation results supporting the K-TRACE research project.

## Repository navigation

| Component | Location | Contents |
|---|---|---|
| Original collected telemetry | [collected-telemetry](collected-telemetry/) | Event CSV, JSONL, Prometheus metrics and run ledger |
| Collection evidence | [collection-evidence](collection-evidence/) | Kubernetes nodes, pods and experimental run proofs |
| ML dataset | [ml-dataset](ml-dataset/) | ML-ready data, train/validation/test splits and split-generation script |
| Original Phase 7 files | [phase7](phase7/) | Original collection outputs |
| Original Phase 8 files | [phase8](phase8/) | Original ML preparation package |
| Source corpus | [01_source_corpus](01_source_corpus/) | Security cases, methodology, glossary and ML result summaries |
| Chunk records | [02_chunks](02_chunks/) | RAG corpus chunk records |
| Sparse retrieval | [03_sparse_retrieval](03_sparse_retrieval/) | BM25 chunks and metadata |
| Retrieval evaluation | [04_retrieval_evaluation](04_retrieval_evaluation/) | Retrieval comparisons, metrics, ablations and grounding analysis |
| Technical documentation | [05_documentation](05_documentation/) | Vector-store design and supporting reports |

## Dataset overview and integrity

- [DATASET_OVERVIEW.md](DATASET_OVERVIEW.md): dataset organization, collection provenance, attack scenarios and ML splits.
- [DATASET_MANIFEST.csv](DATASET_MANIFEST.csv): SHA256 checksums and file sizes for the organized telemetry, evidence and ML files.

## Collected telemetry

The collected event dataset contains 74,212 records. The Prometheus metrics dataset contains 12,390 records.

The recorded experimental scenarios include:

- Benign baseline
- A1: Port scan
- A2: HTTP flood
- A3: Invalid request spray
- A4: Runtime reconnaissance
- A5: Lateral movement
- A6: Exploit-like payloads

## Machine-learning dataset

The supplied ML dataset contains 74,212 records using five features:

`latency_ms`, `bytes_in`, `bytes_out`, `status_code`, `attack_label`.

The supplied partitions contain:

| Partition | Records |
|---|---:|
| Training | 47,495 |
| Validation | 11,874 |
| Testing | 14,843 |
| Total | 74,212 |

## RAG and retrieval artifacts

The retrieval pipeline artifacts are organized into:

1. Source corpus
2. Chunk records
3. BM25 sparse retrieval data
4. Retrieval evaluation outputs
5. Supporting technical documentation

The repository includes chunk records and sparse BM25 data. A serialized dense vector index is not currently included in this directory.

## Data provenance

The original Phase 7 and Phase 8 folders are retained. The organized telemetry directory contains canonical copies of the shared event and Prometheus CSV files.

The duplicate copies were compared using SHA256 and found identical. The original phase folders have not been modified.

## Reproducibility notes

The manifest provides checksums for the organized dataset files. Researchers should verify these before using the data.

The supplied split files document the available partitions. The split-generation methodology and potential data leakage should be independently assessed before drawing conclusions about model generalization.

Retrieval metrics and reports should be interpreted alongside their corresponding evaluation configurations and ground-truth definitions.

