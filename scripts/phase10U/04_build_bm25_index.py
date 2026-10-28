#!/usr/bin/env python3
"""
Phase 10U Part B - Build a persistent BM25 index over v2 chunks.

Reads:
  - artifacts/phase10U/chunks/chunk_records_v2.jsonl

Writes:
  - artifacts/phase10U/bm25/bm25_index.pkl (BM25Okapi instance)
  - artifacts/phase10U/bm25/bm25_chunks.jsonl (chunk-id-to-text mapping)
  - artifacts/phase10U/bm25/bm25_meta.json (index parameters and provenance)

Tokenization is deliberately simple: lowercase, then split on non-alphanumeric.
This matches the Sec-Llama and standard IR research convention for BM25 baselines.
"""
from __future__ import annotations

import json
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path

from rank_bm25 import BM25Okapi

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CHUNKS = ROOT / "artifacts" / "phase10U" / "chunks" / "chunk_records_v2.jsonl"
BM25_DIR = ROOT / "artifacts" / "phase10U" / "bm25"
BM25_INDEX = BM25_DIR / "bm25_index.pkl"
BM25_CHUNKS = BM25_DIR / "bm25_chunks.jsonl"
BM25_META = BM25_DIR / "bm25_meta.json"

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def main():
    BM25_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    print(f"LOADED_CHUNKS: {len(records)}")

    # Build the BM25 corpus: a list of token lists in the same order as records.
    tokenized_corpus = [tokenize(r["text"]) for r in records]
    bm25 = BM25Okapi(tokenized_corpus)

    # Persist the BM25 index.
    with BM25_INDEX.open("wb") as f:
        pickle.dump(bm25, f)

    # Persist the chunk-id-to-text mapping in stable order.
    with BM25_CHUNKS.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({
                "chunk_id": r["chunk_id"],
                "doc_name": r["doc_name"],
                "section": r["section"],
                "family": r.get("family", "UNKNOWN"),
                "doc_type": r.get("doc_type", ""),
                "text": r["text"],
            }) + "\n")

    # Persist provenance.
    BM25_META.write_text(json.dumps({
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "chunk_count": len(records),
        "tokenizer": "lowercase_alnum_split",
        "library": "rank_bm25.BM25Okapi",
        "chunks_source": str(CHUNKS),
    }, indent=2), encoding="utf-8")

    print(f"WROTE_INDEX: {BM25_INDEX}")
    print(f"WROTE_CHUNKS: {BM25_CHUNKS}")
    print(f"WROTE_META: {BM25_META}")

    # Self-test: load index back and run a probe query against an A3 term.
    with BM25_INDEX.open("rb") as f:
        loaded = pickle.load(f)
    probe = "runtime reconnaissance Falco shell"
    scores = loaded.get_scores(tokenize(probe))
    pairs = sorted(
        ((records[i]["chunk_id"], records[i].get("family", "?"), float(s))
         for i, s in enumerate(scores)),
        key=lambda x: -x[2],
    )[:5]
    print("PROBE_QUERY:", probe)
    print("TOP5_PROBE:")
    for cid, fam, score in pairs:
        print(f"  {cid:<40} family={fam:<8} score={score:.3f}")


if __name__ == "__main__":
    main()
