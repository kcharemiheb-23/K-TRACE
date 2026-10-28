#!/usr/bin/env python3
from pathlib import Path
import csv
from collections import defaultdict, Counter

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

RANKED = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_ranked_results.csv"
GT = ROOT / "artifacts" / "phase10R" / "scoring" / "retriever_ground_truth.csv"

OUT_QUERY = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_by_query.csv"
OUT_SUMMARY = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_summary.csv"
OUT_ERRORS = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_error_analysis.csv"

K_VALUES = [1, 3, 5, 10]

def as_int(x):
    try:
        return int(x)
    except Exception:
        return 0

def as_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

ranked = list(csv.DictReader(open(RANKED, newline="", encoding="utf-8")))
gt_rows = list(csv.DictReader(open(GT, newline="", encoding="utf-8")))

relevant_by_query = defaultdict(set)
for r in gt_rows:
    if str(r.get("relevance", "1")) == "1":
        relevant_by_query[r["query_id"]].add(r["chunk_id"])

ranked_by_query = defaultdict(list)
for r in ranked:
    ranked_by_query[r["query_id"]].append(r)

for qid in ranked_by_query:
    ranked_by_query[qid].sort(key=lambda r: as_int(r["rank"]))

metric_rows = []
error_rows = []

for qid, rows in sorted(ranked_by_query.items()):
    relevant = relevant_by_query.get(qid, set())
    total_relevant = len(relevant)

    first = rows[0] if rows else {}
    expected_family = first.get("expected_family", "")
    query_type = first.get("query_type", "")
    run_id = first.get("run_id", "")
    expected_class = first.get("expected_class", "")

    first_rel_rank = None
    for r in rows:
        if r["chunk_id"] in relevant:
            first_rel_rank = as_int(r["rank"])
            break

    reciprocal_rank = 0.0 if first_rel_rank is None else 1.0 / first_rel_rank

    row = {
        "query_id": qid,
        "run_id": run_id,
        "query_type": query_type,
        "expected_class": expected_class,
        "expected_family": expected_family,
        "total_relevant_ground_truth": total_relevant,
        "first_relevant_rank": first_rel_rank if first_rel_rank is not None else "",
        "reciprocal_rank": reciprocal_rank,
    }

    for k in K_VALUES:
        top = rows[:k]
        retrieved_ids = [r["chunk_id"] for r in top]
        relevant_retrieved = sum(1 for cid in retrieved_ids if cid in relevant)

        precision = relevant_retrieved / k if k else 0.0
        recall = relevant_retrieved / total_relevant if total_relevant else 0.0
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

        same_family = sum(as_int(r["same_family_flag"]) for r in top) / k if k else 0.0
        contamination = sum(as_int(r["cross_class_contamination_flag"]) for r in top) / k if k else 0.0
        self_hit = sum(as_int(r["self_hit_flag"]) for r in top) / k if k else 0.0
        benign_attack_contam = sum(as_int(r["benign_attack_contamination_flag"]) for r in top) / k if k else 0.0
        unique_docs = len(set(r["doc_name"] for r in top))
        evidence_diversity = unique_docs / k if k else 0.0

        row[f"precision_at_{k}"] = precision
        row[f"recall_at_{k}"] = recall
        row[f"f1_at_{k}"] = f1
        row[f"same_family_ratio_at_{k}"] = same_family
        row[f"cross_class_contamination_at_{k}"] = contamination
        row[f"self_hit_ratio_at_{k}"] = self_hit
        row[f"benign_attack_contamination_at_{k}"] = benign_attack_contam
        row[f"evidence_diversity_at_{k}"] = evidence_diversity

    metric_rows.append(row)

    if row["precision_at_5"] < 0.5 or row["recall_at_5"] < 0.3 or row["cross_class_contamination_at_5"] > 0.4:
        error_rows.append({
            "query_id": qid,
            "run_id": run_id,
            "query_type": query_type,
            "expected_family": expected_family,
            "precision_at_5": row["precision_at_5"],
            "recall_at_5": row["recall_at_5"],
            "mrr": reciprocal_rank,
            "cross_class_contamination_at_5": row["cross_class_contamination_at_5"],
            "self_hit_ratio_at_5": row["self_hit_ratio_at_5"],
            "weakness_type": "low_precision_or_recall_or_high_contamination",
            "interpretation": "Retriever may be returning weak or class-contaminated evidence for this query."
        })

fieldnames = list(metric_rows[0].keys()) if metric_rows else []
with open(OUT_QUERY, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(metric_rows)

summary_rows = []

def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0

groups = {
    "ALL": metric_rows,
}

for qt in sorted(set(r["query_type"] for r in metric_rows)):
    groups[f"query_type={qt}"] = [r for r in metric_rows if r["query_type"] == qt]

for fam in sorted(set(r["expected_family"] for r in metric_rows)):
    groups[f"expected_family={fam}"] = [r for r in metric_rows if r["expected_family"] == fam]

for group_name, rows in groups.items():
    s = {
        "group": group_name,
        "query_count": len(rows),
        "MRR": mean(as_float(r["reciprocal_rank"]) for r in rows),
    }
    for k in K_VALUES:
        for metric in [
            "precision_at", "recall_at", "f1_at", "same_family_ratio_at",
            "cross_class_contamination_at", "self_hit_ratio_at",
            "benign_attack_contamination_at", "evidence_diversity_at"
        ]:
            col = f"{metric}_{k}"
            s[col] = mean(as_float(r[col]) for r in rows)
    summary_rows.append(s)

summary_fields = list(summary_rows[0].keys()) if summary_rows else []
with open(OUT_SUMMARY, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=summary_fields)
    w.writeheader()
    w.writerows(summary_rows)

error_fields = [
    "query_id", "run_id", "query_type", "expected_family", "precision_at_5",
    "recall_at_5", "mrr", "cross_class_contamination_at_5",
    "self_hit_ratio_at_5", "weakness_type", "interpretation"
]
with open(OUT_ERRORS, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=error_fields)
    w.writeheader()
    w.writerows(error_rows)

print("WROTE:", OUT_QUERY)
print("WROTE:", OUT_SUMMARY)
print("WROTE:", OUT_ERRORS)
print("QUERIES_SCORED:", len(metric_rows))
print("WEAK_QUERIES:", len(error_rows))
