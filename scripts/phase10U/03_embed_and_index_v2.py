#!/usr/bin/env python3
"""
Phase 10U Part B - Embed v2 chunks into a parallel Chroma collection.

Reads:
  - artifacts/phase10U/chunks/chunk_records_v2.jsonl

Writes:
  - artifacts/phase10U/vectorstore_v2/ (PersistentClient path)
  - Chroma collection: ids_rag_corpus_v2

Embedding model: sentence-transformers/all-MiniLM-L6-v2 (matches Phase 10B).
The Phase 10B baseline collection at artifacts/phase10B/vectorstore is NOT touched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CHUNKS = ROOT / "artifacts" / "phase10U" / "chunks" / "chunk_records_v2.jsonl"
VSTORE = ROOT / "artifacts" / "phase10U" / "vectorstore_v2"
COLLECTION_NAME = "ids_rag_corpus_v2"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_records():
    records = []
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def main():
    if not CHUNKS.exists():
        print(f"ERROR: chunk file not found: {CHUNKS}", file=sys.stderr)
        sys.exit(1)

    records = load_records()
    print(f"LOADED_CHUNKS: {len(records)}")

    import chromadb
    from chromadb.utils import embedding_functions

    VSTORE.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VSTORE))

    # If the collection exists from a previous run, recreate it to ensure clean state.
    existing = [c.name if hasattr(c, "name") else str(c) for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"DROPPING_EXISTING: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"phase": "10U", "embedding_model": EMBED_MODEL},
    )
    print(f"CREATED_COLLECTION: {COLLECTION_NAME}")

    # Build parallel arrays for batch insertion.
    ids = [r["chunk_id"] for r in records]
    docs = [r["text"] for r in records]
    metas = []
    for r in records:
        metas.append({
            "doc_name": r.get("doc_name", ""),
            "doc_stem": r.get("doc_stem", ""),
            "section": r.get("section", ""),
            "source_path": r.get("source_path", ""),
            "family": r.get("family", "UNKNOWN"),
            "class_label": r.get("class_label", ""),
            "intensity": r.get("intensity", "none"),
            "run_id": r.get("run_id", ""),
            "doc_type": r.get("doc_type", ""),
            "chunk_index": int(r.get("chunk_index", 1)),
        })

    # Insert in modest batches to keep memory predictable.
    BATCH = 64
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            documents=docs[i:i + BATCH],
            metadatas=metas[i:i + BATCH],
        )

    count = collection.count()
    print(f"COLLECTION_COUNT: {count}")

    # Sanity: pull one item back and show its metadata keys.
    sample = collection.get(ids=[ids[0]], include=["metadatas", "documents"])
    print(f"SAMPLE_ID: {sample['ids'][0]}")
    print(f"SAMPLE_METADATA_KEYS: {list((sample['metadatas'][0] or {}).keys())}")


if __name__ == "__main__":
    main()
