# K-TRACE Paper-to-Evidence Map

This document maps the research questions and reported results in the K-TRACE manuscript to the implementation, experimental inputs, and retained outputs in this repository.

All paths and metrics must be verified against the publication version before this map is considered complete.

## RQ1 — Intrusion Detection

**Reported metrics:** Accuracy, Macro F1, ROC-AUC, PR-AUC, and attack-family classification metrics.

**Evidence to locate:**
- Run-level dataset and data-generation procedure
- Train/validation/test split definitions
- Feature construction and preprocessing code
- Model training and evaluation scripts
- Saved predictions and metric outputs

**Verification status:** Pending.

## RQ2 — Evidence Retrieval

**Reported metrics:** MRR, Precision@5, Recall@5, F1@5, and Contamination@5.

**Evidence to locate:**
- Corpus snapshot and corpus-generation procedure
- Query benchmark and relevance annotations
- Retrieval configurations and evaluation scripts
- Baseline and ablation results
- Confidence intervals and query-level outputs, where available

**Verification status:** Pending.

**Important distinction:** Diagnostic results that use ground-truth family metadata must be distinguished from results obtained using predicted family metadata.

## RQ3 — Grounded LLM Analysis

**Reported evaluation:** Grounding assessment over 14 evaluated cases.

**Evidence to locate:**
- Persisted model generations
- Retrieved evidence associated with each generation
- Grounding-scoring implementation
- Per-case scores and aggregate results
- Model and generation settings, where recorded

**Verification status:** Pending.

The repository documentation must accurately describe the grounding metric and must not present lexical overlap as proof of semantic entailment.

## RQ4 — Controlled Response

**Reported evaluation:** Integrated response benchmark over 11 runs.

**Evidence to locate:**
- Deterministic response policy definitions
- Orchestration and evaluation scripts
- Integrated test cases and run identifiers
- Generated remediation artifacts
- Client-side dry-run outputs and decision traces

**Verification status:** Pending.

Client-side dry-run validation must not be described as proof of successful live-cluster remediation.

## Consistency checks

Before publication, verify that:
- The corpus size agrees between the manuscript, configuration, and evaluation outputs.
- Every reported metric can be traced to a retained output or documented calculation.
- Evaluation splits and run identifiers are consistent.
- The available artifacts match the stated experimental scope.
- Missing data, dependencies, and version information are documented honestly.

## Verification policy

A result is marked **Verified** only after its evidence files have been located and checked. The presence of a script or a previously generated result does not, by itself, prove independent reproducibility.
