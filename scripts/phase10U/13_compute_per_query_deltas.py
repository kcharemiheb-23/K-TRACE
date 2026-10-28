#!/usr/bin/env python3
"""
Phase 10U Part D - Per-query deltas: baseline vs rrf_plus_metadata_rerank.

For every individual query, compute the change in MRR, Precision@5, Recall@5,
and cross_class_contamination_at_5 between the Phase 10R baseline and the
final upgraded mode. Sort by largest improvement so the supervisor demo can
point to specific queries that improved most.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
OUT_BASE = ROOT / "artifacts/phase10U/output"


def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def load(mode):
    p = OUT_BASE / f"scoring_{mode}" / "retrieval_metrics_by_query.csv"
    return {r["query_id"]: r for r in csv.DictReader(p.open())}


METRICS = ["reciprocal_rank", "precision_at_5", "recall_at_5",
           "cross_class_contamination_at_5", "f1_at_5"]


def main():
    base = load("baseline")
    upg = load("rrf_plus_metadata_rerank")
    rows = []
    for qid in sorted(base.keys()):
        b = base[qid]
        u = upg.get(qid)
        if u is None:
            continue
        row = {
            "query_id": qid,
            "run_id": b.get("run_id", ""),
            "query_type": b.get("query_type", ""),
            "expected_family": b.get("expected_family", ""),
        }
        for m in METRICS:
            bm = to_float(b[m])
            um = to_float(u[m])
            row[f"{m}_baseline"] = round(bm, 4)
            row[f"{m}_upgrade"] = round(um, 4)
            row[f"{m}_delta"] = round(um - bm, 4)
        rows.append(row)

    rows.sort(key=lambda r: -r["f1_at_5_delta"])
    out = OUT_BASE / "comparison_per_query_deltas.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE: {out}")
    print(f"\nTop-10 most improved queries by F1@5 delta:")
    print(f"{'query_id':<8} {'family':<8} {'F1@5 base':>10} {'F1@5 upg':>10} {'delta':>10}")
    for r in rows[:10]:
        print(f"{r['query_id']:<8} {r['expected_family']:<8} "
              f"{r['f1_at_5_baseline']:>10.3f} {r['f1_at_5_upgrade']:>10.3f} "
              f"{r['f1_at_5_delta']:>+10.3f}")


if __name__ == "__main__":
    main()
