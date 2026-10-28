#!/usr/bin/env python3
from pathlib import Path
import json
import chromadb

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

VSTORE = ROOT / "artifacts" / "phase10B" / "vectorstore"
OUTDIR = ROOT / "artifacts" / "phase10B" / "chunks"
OUT = OUTDIR / "chunk_records.jsonl"
REPORT = ROOT / "artifacts" / "phase10R" / "reports" / "recovered_chunk_manifest_report.md"

OUTDIR.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(VSTORE))
collections = client.list_collections()

if not collections:
    raise SystemExit("No Chroma collections found.")

collection_name = collections[0].name if hasattr(collections[0], "name") else str(collections[0])
col = client.get_collection(collection_name)

batch = col.get(include=["documents", "metadatas"])
ids = batch.get("ids", [])
docs = batch.get("documents", [])
metas = batch.get("metadatas", [])

rows = []

for i, cid in enumerate(ids):
    meta = metas[i] if i < len(metas) and metas[i] else {}
    text = docs[i] if i < len(docs) else ""

    source_path = meta.get("source_path") or meta.get("path") or meta.get("source") or ""
    doc_name = meta.get("doc_name") or meta.get("filename") or Path(source_path).name or ""
    section = meta.get("section") or meta.get("category") or "unknown"

    rows.append({
        "chunk_id": str(cid),
        "doc_name": doc_name,
        "doc_stem": Path(doc_name).stem if doc_name else "",
        "section": section,
        "source_path": source_path,
        "text": text,
        "metadata": meta,
    })

with open(OUT, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("# Recovered Chunk Manifest from Chroma\n\n")
    f.write(f"- vectorstore: {VSTORE}\n")
    f.write(f"- collection: {collection_name}\n")
    f.write(f"- recovered_rows: {len(rows)}\n")
    f.write(f"- output: {OUT}\n\n")
    f.write("## Expected from Phase 10B report\n\n")
    f.write("- expected_total_chunks: 62\n\n")
    f.write("## Interpretation\n\n")
    if len(rows) == 62:
        f.write("Recovered chunk count matches the Phase 10B chunk report.\n")
    else:
        f.write("Recovered chunk count does not match the Phase 10B chunk report.\n")

print("WROTE:", OUT)
print("WROTE:", REPORT)
print("ROWS:", len(rows))
