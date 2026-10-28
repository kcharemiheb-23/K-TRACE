# Phase 11 — Integrated IDS Response System and Unified Dashboard

## Goal
Turn the validated Phase 10 research pipeline into one orchestrated offline IDS
response workflow with a unified dashboard page. The orchestrator runs the
attack gate, evidence retrieval, LLM explanation, deterministic policy
selection, and dry-run remediation rendering in a single command per run.

## Architecture rules
- ML is the attack gate. BENIGN runs are logged and skipped.
- LLM explains; it does not classify or choose actions.
- Action selection is deterministic and read from a YAML policy file.
- Default remediation mode is dry_run. apply mode requires explicit flag and
  honours a small allowlist of safe targets.
- All Phase 10 artifacts remain untouched. Phase 11 writes only under
  scripts/phase11, artifacts/phase11, docs/proofs/phase11.

## Outputs
- artifacts/phase11/incidents/INC_*.json
- artifacts/phase11/reports/INC_*.md
- artifacts/phase11/actions/INC_*.yaml + INC_*.rollback.sh
- artifacts/phase11/logs/orchestrator_run_*.log
- artifacts/phase11/logs/skipped_benign_*.csv
- artifacts/phase11/summary/phase11_run_summary.csv
- scripts/phase10E/pages/08_Integrated_IDS_Response.py

## Reproducibility
A single shell command (scripts/phase11/demo_run.sh) processes the 11 benchmark
runs and produces the same incident set on every invocation.
