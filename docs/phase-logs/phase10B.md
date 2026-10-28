# Phase 10B - RAG Prototype

## Goal
Build the first working RAG prototype on top of the validated Phase 10A corpus.

## Inputs
- artifacts/phase10A/corpus/*
- artifacts/phase10A/reports/phase10A_source_manifest.md
- artifacts/phase10A/reports/phase10A_corpus_index.md

## Scope
- chunk the corpus
- embed and store the chunks in a vector database
- retrieve top-k evidence for a question
- call a local LLM with retrieved context
- return structured explanation + sources

## Outputs
- chunk manifest
- vector store
- retrieval script
- reasoning script
- saved query examples
- proof files
