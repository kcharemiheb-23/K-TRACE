# Phase 10R - Retriever Inspection, Ground Truth, SMART Metrics, and Dashboard Integration

## Goal
Evaluate the RAG retriever as an independent research component.

## Motivation
The supervisor requested a stronger validation phase focused specifically on the retriever:
- make the retriever visible in the system and dashboard
- explain the search approach
- define the query formulation
- define ground-truth relevant documents
- evaluate ranked results
- compute SMART-style information retrieval metrics

## Inputs
- artifacts/phase10A/corpus
- artifacts/phase10B/chunks/chunk_records.jsonl
- artifacts/phase10B/vectorstore
- artifacts/phase10V/benchmark/validation_benchmark.csv
- artifacts/phase10V/output/*.json
- scripts/phase10E/dashboard_app.py

## Methodology
1. Document the retriever approach.
2. Build benchmark retrieval queries.
3. Define independent ground-truth relevance.
4. Run top-k retrieval inspection.
5. Score Precision@k, Recall@k, F1@k, MRR, and contamination.
6. Write a supervisor-ready retriever evaluation report.
7. Add a retriever evaluation dashboard page.

## Research value
This phase separates retriever behavior from prompt behavior, LLM behavior, and final workflow behavior. It determines whether weak RAG explanations are caused by poor retrieval, poor grounding, or later reasoning errors.

## Expected outputs
- retriever approach report
- retriever benchmark queries
- ground-truth relevance table
- ranked retrieval results
- SMART metric tables
- error analysis
- dashboard data files
- Streamlit retriever evaluation page
