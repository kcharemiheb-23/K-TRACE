#!/usr/bin/env python3
"""
Phase 10U Part D - Headline comparison with bootstrap 95% confidence intervals.

For each mode (baseline, dense_only, bm25_only, rrf, rrf_plus_metadata_rerank)
we read the per-query metrics produced by the Phase 10R scoring code, then for
each headline metric we compute the mean and a 95% bootstrap confidence
interval using 1000 resamples of the 22 queries.

Bootstrap is the right uncertainty quantification here because we have 22
queries and the metrics are not normally distributed. Resampling the queries
with replacement preserves the per-query correlations between metrics.
"""
from __future__ import annotations

import csv
import json
import random
import statistics
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
OUT_BASE = ROOT / "artifacts/phase10U/output"

MODES = ["baseline", "dense_only", "bm25_only", "rrf", "rrf_plus_metadata_rerank"]

HEADLINE_METRICS = [
    "reciprocal_rank",
    "precision_at_5", "recall_at_5", "f1_at_5",
    "precision_at_1", "precision_at_10",
    "same_family_ratio_at_5",
    "cross_class_contamination_at_5",
    "self_hit_ratio_at_5",
    "evidence_diversity_at_5",
]

BOOTSTRAP_N = 1000
SEED = 20260428


def load_per_query(mode: str) -> list[dict]:
    p = OUT_BASE / f"scoring_{mode}" / "retrieval_metrics_by_query.csv"
    return list(csv.DictReader(p.open()))


def to_float(x: str) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def bootstrap_ci(values: list[float], n_iter: int, seed: int):
    """Return (mean, ci_lo, ci_hi) using 95% bootstrap percentile interval."""
    if not values:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_iter):
        sample = [values[rng.randint(0, n - 1)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    return (
        statistics.fmean(values),
        means[int(0.025 * n_iter)],
        means[int(0.975 * n_iter) - 1],
    )


def main():
    rows = []
    for mode in MODES:
        per_query = load_per_query(mode)
        row = {"mode": mode, "n_queries": len(per_query)}
        for metric in HEADLINE_METRICS:
            values = [to_float(r[metric]) for r in per_query]
            mean, lo, hi = bootstrap_ci(values, BOOTSTRAP_N, SEED)
            row[f"{metric}_mean"] = round(mean, 4)
            row[f"{metric}_ci_lo"] = round(lo, 4)
            row[f"{metric}_ci_hi"] = round(hi, 4)
        rows.append(row)

    out = OUT_BASE / "comparison_headline.csv"
    fieldnames = list(rows[0].keys())
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE: {out}")

    # Pretty-print a summary table to stdout.
    print(f"\n{'mode':<28} {'MRR':>16} {'P@5':>16} {'R@5':>16} {'F1@5':>16} {'CrossContam@5':>18}")
    print("-" * 120)
    for r in rows:
        def fmt(metric):
            return f"{r[metric+'_mean']:.3f} [{r[metric+'_ci_lo']:.3f}-{r[metric+'_ci_hi']:.3f}]"
        print(f"{r['mode']:<28} "
              f"{fmt('reciprocal_rank'):>16} "
              f"{fmt('precision_at_5'):>16} "
              f"{fmt('recall_at_5'):>16} "
              f"{fmt('f1_at_5'):>16} "
              f"{fmt('cross_class_contamination_at_5'):>18}")


if __name__ == "__main__":
    main()
