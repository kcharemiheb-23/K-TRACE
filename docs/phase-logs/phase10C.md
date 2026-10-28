# Phase 10C - Multi-Model LLM Evaluation

## Goal
Evaluate the Phase 10B RAG reasoning pipeline across multiple local LLMs.

## Inputs
- artifacts/phase10A/corpus/*
- artifacts/phase10B/vectorstore/*
- scripts/phase10B/05_reason_with_rag.py
- local Ollama models

## Evaluation targets
- correctness
- grounding in retrieved evidence
- consistency with ML-oriented project context
- hallucination resistance
- usefulness to a security analyst

## Compared models
- mistral
- phi3:mini

## Outputs
- fixed evaluation question set
- per-model saved answers
- scoring table
- aggregate comparison results
- final supervisor-ready summary
