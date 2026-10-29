# Extracted Methodology Document

**Source path:** `./docs/phase-logs/phase9.md`

---

# Phase 9 - Traditional ML Validation

## Goal
Validate the Phase 8 dataset with leakage-safe traditional ML experiments.

## Inputs
- artifacts/phase8/output/feature_dataset_binary.csv
- artifacts/phase8/output/feature_dataset_multiclass.csv
- artifacts/phase8/output/split_train_runs.csv
- artifacts/phase8/output/split_val_runs.csv
- artifacts/phase8/output/split_test_runs.csv

## Tasks
- Binary classification: BENIGN vs ATTACK
- Multiclass classification: BENIGN + A1 + A2 + A3 + A4

## Planned models
- LogisticRegression
- DecisionTree
- RandomForest
- ExtraTrees
- HistGradientBoosting
- SVC

## Outputs
- metrics CSVs
- classification reports
- confusion matrices
- ROC and PR curves for binary
- feature importance plots
- experiment summary
