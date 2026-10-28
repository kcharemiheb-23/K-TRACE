# Phase 8 - Dataset QC and Feature Engineering

## Goal
Convert the validated Phase 7 raw corpus into a clean, manifest-driven, trim-aware, leakage-safe ML dataset.

## Trusted inputs
- scripts/phase7/plans/full_plan.csv
- artifacts/phase7/output/dataset_run_manifest_clean.csv
- artifacts/phase7/raw/<RUN_ID>/*

## Main requirements
- official full-plan runs only
- manifest-driven labels
- trim-aware structured parsing
- unified dataset for binary and multiclass tasks
- grouped splits by run_id
- documentation and QC reports

## Planned outputs
- structured_envoy.csv
- structured_falco.csv
- structured_prometheus.csv
- run_feature_dataset.csv
- feature_dataset_binary.csv
- feature_dataset_multiclass.csv
- split_train_runs.csv
- split_val_runs.csv
- split_test_runs.csv
- phase8_qc_report.md
