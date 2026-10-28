#!/usr/bin/env python3
"""
Phase 10U Part D - Per-family decomposition across all modes.

For each (mode, family) pair, compute mean precision_at_5, recall_at_5,
f1_at_5, MRR, and cross_class_contamination_at_5. Output a long-form CSV with
one row per (mode, family) so the dashboard and the report can pivot on it.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
OUT_BASE = ROOT / "artifacts/phase10U/output"
MODES = ["baseline", "dense_only", "bm25_only", "rrf", "rrf_plus_metadata_rerank"]
METRICS = [
    "reciprocal_rank", "precision_at_5", "recall_at_5", "f1_at_5",
    "same_family_ratio_at_5", "cross_class_contamination_at_5",
]


def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def main():
    rows = []
    for mode in MODES:
        path = OUT_BASE / f"scoring_{mode}" / "retrieval_metrics_by_query.csv"
        per_query = list(csv.DictReader(path.open()))
        by_family = {}
        for r in per_query:
            fam = r["expected_family"]
            by_family.setdefault(fam, []).append(r)
        for fam, qs in by_family.items():
            row = {"mode": mode, "family": fam, "n_queries": len(qs)}
            for m in METRICS:
                values = [to_float(q[m]) for q in qs]
                row[m] = round(sum(values) / len(values), 4) if values else 0.0
            rows.append(row)

    out = OUT_BASE / "comparison_per_family.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE: {out}")

    # Print a pivot focused on Precision@5.
    print("\nPrecision@5 by family across modes:")
    families = sorted(set(r["family"] for r in rows))
    print(f"{'mode':<28} " + " ".join(f"{fam:>10}" for fam in families))
    for mode in MODES:
        cells = []
        for fam in families:
            v = next((r["precision_at_5"] for r in rows
                      if r["mode"] == mode and r["family"] == fam), None)
            cells.append(f"{v:>10.3f}" if v is not None else f"{'-':>10}")
        print(f"{mode:<28} " + " ".join(cells))


if __name__ == "__main__":
    main()
