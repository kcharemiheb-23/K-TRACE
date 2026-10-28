#!/usr/bin/env python3
"""
Phase 10U Part D - Ablation study.

Compares the four upgrade modes against the baseline as cumulative levers:

  baseline                         (Phase 10R: dense over Phase 10A boilerplate corpus)
  dense_only                       (+ corpus enrichment)
  bm25_only                        (lexical signal alone, on enriched corpus)
  rrf                              (+ hybrid fusion)
  rrf_plus_metadata_rerank         (+ metadata-aware reranking)

Each row reports the change in headline metrics versus the previous lever, so
you can see whether each lever contributed independently. This is the
academic-grade evidence that the upgrade is not just working by accident.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
OUT_BASE = ROOT / "artifacts/phase10U/output"

# The "lever order" is what we tell readers represents progressive enhancement.
LEVER_ORDER = [
    ("baseline", "Phase 10R baseline (dense, Phase 10A corpus)"),
    ("dense_only", "+ corpus enrichment (Part A)"),
    ("bm25_only", "lexical-only on enriched corpus"),
    ("rrf", "+ hybrid fusion via Reciprocal Rank Fusion"),
    ("rrf_plus_metadata_rerank", "+ metadata-aware reranking"),
]

METRICS = ["reciprocal_rank", "precision_at_5", "recall_at_5", "f1_at_5",
           "cross_class_contamination_at_5"]


def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def mode_means(mode):
    p = OUT_BASE / f"scoring_{mode}" / "retrieval_metrics_by_query.csv"
    rows = list(csv.DictReader(p.open()))
    out = {}
    for m in METRICS:
        vals = [to_float(r[m]) for r in rows]
        out[m] = sum(vals) / len(vals) if vals else 0.0
    return out


def main():
    out_rows = []
    prev = None
    for mode, label in LEVER_ORDER:
        means = mode_means(mode)
        row = {"lever": label, "mode": mode}
        for m in METRICS:
            row[f"{m}_mean"] = round(means[m], 4)
            row[f"{m}_delta_vs_prev"] = (
                round(means[m] - prev[m], 4) if prev is not None else 0.0
            )
        out_rows.append(row)
        prev = means

    out = OUT_BASE / "ablation_study.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"WROTE: {out}\n")

    # Pretty print
    print(f"{'lever':<55} {'F1@5':>8} {'dF1@5':>8} {'P@5':>8} {'R@5':>8} {'MRR':>8}")
    print("-" * 100)
    for r in out_rows:
        print(f"{r['lever']:<55} "
              f"{r['f1_at_5_mean']:>8.3f} "
              f"{r['f1_at_5_delta_vs_prev']:>+8.3f} "
              f"{r['precision_at_5_mean']:>8.3f} "
              f"{r['recall_at_5_mean']:>8.3f} "
              f"{r['reciprocal_rank_mean']:>8.3f}")


if __name__ == "__main__":
    main()
