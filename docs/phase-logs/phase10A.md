# Phase 10A - RAG Knowledge Base Construction

## Goal
Build the offline RAG knowledge base from validated project artifacts.

## Inputs
- artifacts/phase8/output/run_feature_dataset.csv
- artifacts/phase8/output/split_test_runs.csv
- artifacts/phase9_v2/output/*.csv
- artifacts/phase9_v2/reports/*.md
- docs/phase-logs/phase9.md
- docs/phase-logs/phase9_v2.md

## Scope
This phase does not build embeddings yet.
It builds the document corpus that will later be chunked, embedded, and indexed.

## Corpus families
- methodology
- features
- ml_results
- cases
- glossary

## Outputs
- source manifest
- methodology docs extracted from environment
- feature dictionary built from dataset columns
- ML result docs extracted from validated outputs
- case docs built from test-set runs and model predictions
- corpus index and counts
