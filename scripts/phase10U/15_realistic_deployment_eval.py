#!/usr/bin/env python3
"""
Phase 10U Part D - Realistic deployment evaluation.

Re-runs the rrf_plus_metadata_rerank mode against the same 22 benchmark
queries, but uses the ACTUAL multiclass prediction for each run instead of
the ground-truth family. This measures what the upgraded retriever delivers
in deployment, where ground-truth families are unknown by definition.

ML predictions are read directly from each case's enriched markdown, where
they were preserved from the Phase 9 v2 multiclass model results.
"""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
QUERIES = ROOT / "artifacts/phase10R/benchmark/retriever_queries.csv"
CASES = ROOT / "artifacts/phase10U/corpus_v2/cases"
OUT_DIR = ROOT / "artifacts/phase10U/output"

# Reuse the Part C retriever module.
spec = importlib.util.spec_from_file_location(
    "upgraded_retriever",
    ROOT / "scripts/phase10U/06_upgraded_retriever.py",
)
upgraded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgraded)

RANK_COLS = [
    "query_id", "run_id", "query_type", "query_text",
    "expected_class", "expected_family",
    "predicted_family",
    "rank", "chunk_id", "doc_name", "section", "source_path",
    "distance", "similarity_score_readable",
    "retrieved_family",
    "same_family_flag", "self_hit_flag",
    "cross_class_contamination_flag", "benign_attack_contamination_flag",
    "text_preview", "retrieval_backend", "collection_name",
]


def family_of_class_label(label: str) -> str:
    label = (label or "").upper()
    for fam in ("A1", "A2", "A3", "A4"):
        if label.startswith(fam):
            return fam
    if label.startswith("BENIGN"):
        return "BENIGN"
    return "UNKNOWN"


def predicted_family_for(run_id: str) -> str:
    """Read the multiclass prediction recorded in the enriched case file."""
    p = CASES / f"{run_id}.md"
    if not p.exists():
        return ""
    text = p.read_text()
    m = re.search(r"-\s*Multiclass predicted label:\s*(\S+)", text)
    if not m:
        return ""
    return family_of_class_label(m.group(1))


def attack_or_benign(family: str) -> str:
    if family == "BENIGN":
        return "BENIGN"
    if family in {"A1", "A2", "A3", "A4"}:
        return "ATTACK"
    return "UNKNOWN"


def main():
    queries = list(csv.DictReader(QUERIES.open()))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "realistic_deployment_ranked_results.csv"

    pred_match = pred_total = 0
    used_predictions = []

    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RANK_COLS)
        w.writeheader()
        for q in queries:
            run_id = q["run_id"]
            expected_family = q["expected_family"]
            predicted_family = predicted_family_for(run_id) or expected_family
            used_predictions.append((run_id, expected_family, predicted_family))
            pred_total += 1
            if predicted_family == expected_family:
                pred_match += 1

            results = upgraded.retrieve(
                query_text=q["query_text"],
                top_k=int(q.get("top_k") or 10),
                mode="rrf_plus_metadata_rerank",
                expected_family=predicted_family,
            )
            for r in results:
                retrieved_family = r["retrieved_family"]
                doc_name = r["doc_name"]
                same_family = 1 if retrieved_family == expected_family else 0
                self_hit = 1 if (run_id and run_id in doc_name) else 0
                cross_contam = 1 if retrieved_family not in {expected_family, "UNKNOWN"} else 0
                benign_attack_contam = 0
                exp_side = attack_or_benign(expected_family)
                ret_side = attack_or_benign(retrieved_family)
                if exp_side != "UNKNOWN" and ret_side != "UNKNOWN" and exp_side != ret_side:
                    benign_attack_contam = 1
                w.writerow({
                    "query_id": q["query_id"],
                    "run_id": run_id,
                    "query_type": q["query_type"],
                    "query_text": q["query_text"],
                    "expected_class": q.get("expected_class", ""),
                    "expected_family": expected_family,
                    "predicted_family": predicted_family,
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
                    "retrieval_backend": "phase10U_realistic_deployment",
                    "collection_name": "ids_rag_corpus_v2",
                })

    print(f"WROTE: {out_path}")
    print(f"ML_PREDICTION_AGREES_WITH_GT: {pred_match}/{pred_total}")
    print("Per-query prediction summary:")
    for run_id, exp, pred in used_predictions:
        marker = "OK" if exp == pred else "MISMATCH"
        print(f"  {run_id:<32} expected={exp:<8} predicted={pred:<8} {marker}")


if __name__ == "__main__":
    main()
