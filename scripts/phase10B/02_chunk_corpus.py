#!/usr/bin/env python3
from pathlib import Path
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
CORPUS = ROOT / "artifacts" / "phase10A" / "corpus"
OUT = ROOT / "artifacts" / "phase10B" / "chunks" / "chunk_records.jsonl"
REPORT = ROOT / "artifacts" / "phase10B" / "reports" / "phase10B_chunk_report.md"

MAX_CHARS = 900
OVERLAP = 120

def iter_docs():
    for section in ["methodology", "features", "ml_results", "cases", "glossary"]:
        for path in sorted((CORPUS / section).glob("*.md")):
            yield section, path

def chunk_text(text, max_chars=MAX_CHARS, overlap=OVERLAP):
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

chunk_rows = []
doc_count = 0

for section, path in iter_docs():
    text = path.read_text()
    parts = chunk_text(text)
    doc_count += 1
    for i, part in enumerate(parts, start=1):
        chunk_id = f"{path.stem}_chunk{i}"
        row = {
            "chunk_id": chunk_id,
            "doc_name": path.name,
            "doc_stem": path.stem,
            "section": section,
            "source_path": str(path),
            "text": part,
        }
        chunk_rows.append(row)

with open(OUT, "w") as f:
    for row in chunk_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

with open(REPORT, "w") as f:
    f.write("# Phase 10B Chunk Report\n\n")
    f.write(f"- total_documents: {doc_count}\n")
    f.write(f"- total_chunks: {len(chunk_rows)}\n")
    f.write(f"- max_chars: {MAX_CHARS}\n")
    f.write(f"- overlap: {OVERLAP}\n\n")

    by_section = {}
    for row in chunk_rows:
        by_section[row["section"]] = by_section.get(row["section"], 0) + 1

    f.write("## chunks_by_section\n")
    for k, v in sorted(by_section.items()):
        f.write(f"- {k}: {v}\n")

print("WROTE:", OUT)
print("WROTE:", REPORT)
