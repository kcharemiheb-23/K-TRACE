#!/usr/bin/env python3
"""
Phase 10U Part C - Run the upgraded retriever against the Phase 10R benchmark
queries in all four modes and write ranked-results CSVs in the same schema as
Phase 10R, so the existing scoring pipeline can consume them directly.

Modes run:
  dense_only, bm25_only, rrf, rrf_plus_metadata_rerank

For rrf_plus_metadata_rerank, expected_family is taken directly from the query
benchmark file. For other modes expected_family is None, so the scoring step
later compares each mode to the same ground truth fairly.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path.home() / "cloud-native-ids-azure" / "scripts" / "phase10U"),
)

# Import after sys.path tweak so Python finds the module by file path.
import importlib.util
spec = importlib.util.spec_from_file_location(
    "upgraded_retriever",
    Path.home() / "cloud-native-ids-azure" / "scripts" / "phase10U" /
    "06_upgraded_retriever.py",
)
upgraded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgraded)

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUERIES = ROOT / "artifacts" / "phase10R" / "benchmark" / "retriever_queries.csv"
OUT_DIR = ROOT / "artifacts" / "phase10U" / "output"

MODES = ["dense_only", "bm25_only", "rrf", "rrf_plus_metadata_rerank"]


# Schema must match Phase 10R retrieval_ranked_results.csv so the scoring
# script consumes our output without modification.
RANK_COLS = [
    "query_id", "run_id", "query_type", "query_text",
    "expected_class", "expected_family",
    "rank", "chunk_id", "doc_name", "section", "source_path",
    "distance", "similarity_score_readable",
    "retrieved_family",
    "same_family_flag", "self_hit_flag",
    "cross_class_contamination_flag", "benign_attack_contamination_flag",
    "text_preview", "retrieval_backend", "collection_name",
]


def attack_or_benign(family: str) -> str:
    if family == "BENIGN":
        return "BENIGN"
    if family in {"A1", "A2", "A3", "A4"}:
        return "ATTACK"
    return "UNKNOWN"


def run_mode(mode: str, queries: list[dict]) -> Path:
    out_path = OUT_DIR / f"retrieval_ranked_results_v2_{mode}.csv"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RANK_COLS)
        writer.writeheader()
        for q in queries:
            top_k = int(q.get("top_k") or 10)
            expected_family = q.get("expected_family", "")
            results = upgraded.retrieve(
                query_text=q["query_text"],
                top_k=top_k,
                mode=mode,
                expected_family=(
                    expected_family if mode == "rrf_plus_metadata_rerank"
                    else None
                ),
            )
            for r in results:
                retrieved_family = r["retrieved_family"]
                doc_name = r["doc_name"]
                same_family = (1 if retrieved_family == expected_family else 0)
                self_hit = 1 if (q["run_id"] and q["run_id"] in doc_name) else 0
                cross_contam = (
                    1 if retrieved_family not in {expected_family, "UNKNOWN"}
                    else 0
                )
                benign_attack_contam = 0
                exp_side = attack_or_benign(expected_family)
                ret_side = attack_or_benign(retrieved_family)
                if (exp_side != "UNKNOWN" and ret_side != "UNKNOWN"
                        and exp_side != ret_side):
                    benign_attack_contam = 1

                writer.writerow({
                    "query_id": q["query_id"],
                    "run_id": q["run_id"],
                    "query_type": q["query_type"],
                    "query_text": q["query_text"],
                    "expected_class": q.get("expected_class", ""),
                    "expected_family": expected_family,
                    "rank": r["rank"],
                    "chunk_id": r["chunk_id"],
                    "doc_name": doc_name,
                    "section": r["section"],
                    "source_path": r["source_path"],
                    "distance": r["distance"],
                    "similarity_score_readable": r["similarity_score_readable"],
                    "retrieved_family": retrieved_family,
                    "same_family_flag": same_family,
                    "self_hit_flag": self_hit,
                    "cross_class_contamination_flag": cross_contam,
                    "benign_attack_contamination_flag": benign_attack_contam,
                    "text_preview": r["text_preview"],
                    "retrieval_backend": f"phase10U_{mode}",
                    "collection_name": "ids_rag_corpus_v2",
                })
                rows_written += 1
    return out_path, rows_written


def main():
    queries = list(csv.DictReader(QUERIES.open(encoding="utf-8")))
    print(f"LOADED_QUERIES: {len(queries)}")
    for mode in MODES:
        path, rows = run_mode(mode, queries)
        print(f"WROTE: {path.name} rows={rows}")


if __name__ == "__main__":
    main()
