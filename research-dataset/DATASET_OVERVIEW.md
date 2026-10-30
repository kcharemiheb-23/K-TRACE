# K-TRACE Research Dataset

## 1. Overview

This directory contains the experimental data and research artifacts used by K-TRACE. It preserves the collected cloud-native security telemetry, the machine-learning dataset derived from that telemetry, collection evidence, and RAG-related artifacts.

The dataset is organized to distinguish original experimental records from processed data and retrieval-evaluation outputs.

## 2. Dataset organization

| Directory | Description |
|---|---|
| `phase7/` | Original Phase 7 collection output |
| `phase8/` | Original Phase 8 ML preparation package |
| `collected-telemetry/` | Organized copy of the original collected telemetry |
| `collection-evidence/` | Kubernetes environment and collection proof files |
| `ml-dataset/` | ML-ready dataset and train/validation/test splits |
| `01_source_corpus/` | Source corpus used by the retrieval pipeline |
| `02_chunks/` | Chunk records |
| `03_sparse_retrieval/` | Sparse BM25 retrieval artifacts |
| `04_retrieval_evaluation/` | Retrieval evaluation results |
| `05_documentation/` | Supporting technical documentation |

The original Phase 7 and Phase 8 folders are retained to preserve experimental provenance.

## 3. Phase 7: Collected telemetry

The Phase 7 collection output includes:

- `dataset_events.csv`
- `dataset_events.jsonl`
- `dataset_metrics_prometheus.csv`
- `run-ledger.csv`

The event dataset contains 74,212 records. The Prometheus metrics dataset contains 12,390 records.

The event CSV includes fields describing timestamps, source and destination workloads, network protocol, HTTP method, response status, latency, transferred bytes, event type, runtime rule, and attack label.

The run ledger records experimental runs and their attack labels.

### 3.1 Experimental scenarios

The collection evidence identifies the following scenarios:

| Label | Scenario |
|---|---|
| `BENIGN_BASELINE` | Benign baseline |
| `A1_PORT_SCAN` | Port scanning |
| `A2_HTTP_FLOOD` | HTTP flood |
| `A3_INVALID_REQUEST_SPRAY` | Invalid request spray |
| `A4_RUNTIME_RECON` | Runtime reconnaissance |
| `A5_LATERAL_MOVEMENT` | Lateral movement |
| `A6_EXPLOIT_LIKE_PAYLOADS` | Exploit-like payloads |

### 3.2 Collection evidence

The `collection-evidence/` directory contains:

- `proof-nodes.txt`
- `proof-pods-all.txt`
- `proof-output-tree.txt`
- `proof-run-ledger.txt`

These files preserve supporting evidence about the Kubernetes environment, workloads, output structure, and experimental runs.

## 4. Phase 8: Machine-learning dataset

The Phase 8 package contains the ML-ready dataset and its split files:

| File | Records |
|---|---:|
| `ml_dataset.csv` | 74,212 |
| `train.csv` | 47,495 |
| `validation.csv` | 11,874 |
| `test.csv` | 14,843 |
| **Total across splits** | **74,212** |

The ML dataset uses five columns:

- `latency_ms`
- `bytes_in`
- `bytes_out`
- `status_code`
- `attack_label`

The package also includes `create_splits.py` and `dataset_description.md`.

The split counts sum to the reported dataset size. This documents the supplied split files; it does not independently establish the split-generation methodology or absence of leakage.

## 5. Data provenance and duplicate files

The Phase 7 and Phase 8 packages contain duplicate copies of:

- `dataset_events.csv`
- `dataset_metrics_prometheus.csv`

Their SHA256 hashes were compared and found identical.

The organized `collected-telemetry/` directory therefore keeps one canonical copy of each, while the original phase folders remain preserved.

`DATASET_MANIFEST.csv` records the SHA256 checksum and file size of each file in the organized telemetry, collection-evidence, and ML dataset directories.

## 6. Relationship to the RAG pipeline

The RAG-related artifacts are maintained separately from the raw telemetry and ML dataset:

1. Source corpus
2. Chunk records
3. Sparse retrieval artifacts
4. Retrieval evaluation results
5. Supporting documentation

This separation makes it possible to distinguish collected experimental telemetry, ML-prepared records, and retrieval-related research artifacts.

The presence of these directories does not by itself establish that every telemetry record was ingested into the RAG corpus. That relationship must be supported by the actual ingestion and transformation records.

## 7. Reproducibility and integrity

Researchers can use the SHA256 values in `DATASET_MANIFEST.csv` to verify the organized dataset files.

The original Phase 7 and Phase 8 folders are retained as provenance references.

For integrity checks, compare the SHA256 checksum of a file against its corresponding manifest entry.

## 8. Important limitations

- The dataset reflects the experimental collection represented by the supplied Phase 7 and Phase 8 artifacts.
- The ML dataset contains a selected five-feature representation of the event data.
- The supplied split files document the available partitioning; additional validation is required before making claims about leakage prevention.
- Retrieval and vector-index artifacts should be interpreted according to the files actually included in the repository.
- Experimental results should be reproduced using the associated scripts and documented configurations before making performance claims.

