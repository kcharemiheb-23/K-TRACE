#!/usr/bin/env python3
"""
Phase 10U Part B - Chunker for the enriched v2 corpus.

Reads:
  - artifacts/phase10U/corpus_v2/{cases,methodology,ml_results,features,glossary}/*.md

Writes:
  - artifacts/phase10U/chunks/chunk_records_v2.jsonl

Chunking rules:
  - Cases: one chunk per case document. This eliminates the boilerplate-tail
    near-duplicate problem that polluted Phase 10R retrieval and is safe
    because the enriched cases stay well under any practical embedding limit.
  - Methodology, ml_results, features, glossary: 900-char windows with 120-char
    overlap to preserve continuity with Phase 10B chunking on these documents.

Per-chunk metadata schema:
  - chunk_id, doc_name, doc_stem, section, source_path
  - text
  - family (A1, A2, A3, A4, BENIGN, UNKNOWN)
  - class_label (e.g. A3_RUNTIME_RECON)
  - intensity (low, medium, high, none)
  - run_id (if a case)
  - doc_type (case, methodology, ml_results, features, glossary)
  - chunk_index (1-based within the document)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CORPUS_V2 = ROOT / "artifacts" / "phase10U" / "corpus_v2"
OUT_JSONL = ROOT / "artifacts" / "phase10U" / "chunks" / "chunk_records_v2.jsonl"

NON_CASE_CHUNK_SIZE = 900
NON_CASE_CHUNK_OVERLAP = 120


def family_of(class_label: str, doc_stem: str) -> str:
    target = (class_label or doc_stem or "").upper()
    if target.startswith("A1"):
        return "A1"
    if target.startswith("A2"):
        return "A2"
    if target.startswith("A3"):
        return "A3"
    if target.startswith("A4"):
        return "A4"
    if target.startswith("BENIGN"):
        return "BENIGN"
    return "UNKNOWN"


def parse_case_metadata(text: str, doc_stem: str) -> dict:
    fields = {}
    patterns = {
        "run_id": r"-\s*run_id:\s*(\S+)",
        "class_label": r"-\s*class_label:\s*(\S+)",
        "intensity": r"-\s*intensity:\s*(\S+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text)
        fields[key] = m.group(1) if m else ""
    if not fields["run_id"]:
        fields["run_id"] = doc_stem
    if not fields["intensity"]:
        fields["intensity"] = "none"
    fields["family"] = family_of(fields["class_label"], doc_stem)
    return fields


def chunk_non_case(text: str, size: int, overlap: int) -> list[str]:
    """Sliding-window character chunker matching Phase 10B parameters."""
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    step = size - overlap
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += step
    return chunks


def section_name_for(doc_type: str) -> str:
    """Match the section taxonomy used in Phase 10B for compatibility."""
    return doc_type


def emit_records():
    records = []

    # Cases: one chunk per case file, full metadata.
    for case_path in sorted((CORPUS_V2 / "cases").glob("*.md")):
        text = case_path.read_text(encoding="utf-8")
        meta = parse_case_metadata(text, case_path.stem)
        rec = {
            "chunk_id": f"{case_path.stem}_chunk1",
            "doc_name": case_path.name,
            "doc_stem": case_path.stem,
            "section": "cases",
            "source_path": str(case_path),
            "text": text,
            "family": meta["family"],
            "class_label": meta["class_label"] or meta["family"],
            "intensity": meta["intensity"],
            "run_id": meta["run_id"],
            "doc_type": "case",
            "chunk_index": 1,
        }
        records.append(rec)

    # Non-case sections: sliding-window chunking matching Phase 10B size and overlap.
    section_dirs = [
        ("methodology", "methodology"),
        ("ml_results", "ml_results"),
        ("features", "features"),
        ("glossary", "glossary"),
    ]
    for sub, section in section_dirs:
        for doc_path in sorted((CORPUS_V2 / sub).glob("*.md")):
            text = doc_path.read_text(encoding="utf-8")
            chunks = chunk_non_case(text, NON_CASE_CHUNK_SIZE, NON_CASE_CHUNK_OVERLAP)
            for idx, chunk_text in enumerate(chunks, start=1):
                rec = {
                    "chunk_id": f"{doc_path.stem}_chunk{idx}",
                    "doc_name": doc_path.name,
                    "doc_stem": doc_path.stem,
                    "section": section_name_for(section),
                    "source_path": str(doc_path),
                    "text": chunk_text,
                    "family": "UNKNOWN",
                    "class_label": "",
                    "intensity": "none",
                    "run_id": "",
                    "doc_type": section,
                    "chunk_index": idx,
                }
                records.append(rec)

    return records


def main():
    records = emit_records()
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_section = {}
    by_family = {}
    by_doctype = {}
    for r in records:
        by_section[r["section"]] = by_section.get(r["section"], 0) + 1
        by_family[r["family"]] = by_family.get(r["family"], 0) + 1
        by_doctype[r["doc_type"]] = by_doctype.get(r["doc_type"], 0) + 1

    print(f"WROTE: {OUT_JSONL}")
    print(f"TOTAL_CHUNKS: {len(records)}")
    print(f"BY_SECTION: {by_section}")
    print(f"BY_FAMILY: {by_family}")
    print(f"BY_DOC_TYPE: {by_doctype}")


if __name__ == "__main__":
    main()
