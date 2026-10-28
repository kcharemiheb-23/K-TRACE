#!/usr/bin/env python3
from pathlib import Path
import json
import chromadb
from sentence_transformers import SentenceTransformer

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
CHUNKS = ROOT / "artifacts" / "phase10B" / "chunks" / "chunk_records.jsonl"
VDBDIR = ROOT / "artifacts" / "phase10B" / "vectorstore"
REPORT = ROOT / "artifacts" / "phase10B" / "reports" / "phase10B_ingest_report.md"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "ids_rag_corpus"

rows = []
with open(CHUNKS, "r") as f:
    for line in f:
        rows.append(json.loads(line))

texts = [r["text"] for r in rows]
ids = [r["chunk_id"] for r in rows]
metadatas = [
    {
        "doc_name": r["doc_name"],
        "doc_stem": r["doc_stem"],
        "section": r["section"],
        "source_path": r["source_path"],
    }
    for r in rows
]

model = SentenceTransformer(MODEL_NAME)
embeddings = model.encode(texts, show_progress_bar=True).tolist()

client = chromadb.PersistentClient(path=str(VDBDIR))
existing = [c.name for c in client.list_collections()]
if COLLECTION_NAME in existing:
    client.delete_collection(COLLECTION_NAME)

collection = client.create_collection(name=COLLECTION_NAME)
collection.add(
    ids=ids,
    documents=texts,
    metadatas=metadatas,
    embeddings=embeddings,
)

with open(REPORT, "w") as f:
    f.write("# Phase 10B Ingest Report\n\n")
    f.write(f"- embedding_model: {MODEL_NAME}\n")
    f.write(f"- collection_name: {COLLECTION_NAME}\n")
    f.write(f"- total_chunks: {len(rows)}\n")
    f.write(f"- vectorstore_path: {VDBDIR}\n")

print("WROTE:", REPORT)
print("INGESTED CHUNKS:", len(rows))
