#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

APPROACH = ROOT / "artifacts" / "phase10R" / "reports" / "retriever_approach.md"
POLICY = ROOT / "artifacts" / "phase10R" / "reports" / "ground_truth_policy.md"
SUMMARY = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_summary.csv"
BY_QUERY = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_by_query.csv"
ERRORS = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_error_analysis.csv"
OUT = ROOT / "artifacts" / "phase10R" / "reports" / "phase10R_retriever_evaluation_report.md"

def read_csv(path):
    if not path.exists():
        return []
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))

summary = read_csv(SUMMARY)
by_query = read_csv(BY_QUERY)
errors = read_csv(ERRORS)

def get_group(name):
    for r in summary:
        if r["group"] == name:
            return r
    return {}

overall = get_group("ALL")

def fmt(x):
    try:
        return f"{float(x):.4f}"
    except Exception:
        return str(x)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Phase 10R Retriever Evaluation Report\n\n")

    f.write("## 1. Purpose\n\n")
    f.write("Phase 10R evaluates the RAG retriever as an independent component of the cloud-native IDS reasoning pipeline. ")
    f.write("This phase was created after supervisor feedback that the retriever and RAG validation were not sufficiently visible or measurable.\n\n")

    f.write("## 2. Retriever approach\n\n")
    f.write("The current retriever is evaluated as a dense semantic vector retriever. ")
    f.write("The retrieval formulation is query embedding versus document-chunk embedding, followed by top-k vector similarity ranking. ")
    f.write("The current system is not evaluated as BM25 or exact keyword retrieval.\n\n")

    f.write("| Search approach | Status |\n")
    f.write("|---|---|\n")
    f.write("| Exact keyword search | Not current approach |\n")
    f.write("| BM25 sparse lexical search | Not current approach |\n")
    f.write("| Dense semantic vector search | Current approach |\n")
    f.write("| Hybrid search | Future upgrade candidate |\n\n")

    f.write("## 3. Ground-truth definition\n\n")
    f.write("Ground truth was defined independently from retrieval output. ")
    f.write("A chunk is relevant when it supports the expected IDS evidence need for the query family. ")
    f.write("Same-family case documents are considered strongly relevant, while methodology, feature, glossary, and result chunks are relevant when they contain family-specific evidence vocabulary.\n\n")

    f.write("## 4. SMART-style retrieval metrics\n\n")
    f.write("The following metrics were computed:\n\n")
    f.write("- **Precision@k**: proportion of top-k retrieved chunks that are relevant.\n")
    f.write("- **Recall@k**: proportion of all ground-truth relevant chunks found in top-k.\n")
    f.write("- **F1@k**: harmonic mean of Precision@k and Recall@k.\n")
    f.write("- **MRR**: mean reciprocal rank of the first relevant result.\n")
    f.write("- **Same-family ratio@k**: proportion of retrieved chunks from the expected class family.\n")
    f.write("- **Cross-class contamination@k**: proportion of retrieved chunks from a wrong attack/benign family.\n")
    f.write("- **Self-hit ratio@k**: proportion of retrieved chunks directly matching the same run ID.\n")
    f.write("- **Evidence diversity@k**: proportion of unique documents in top-k evidence.\n\n")

    f.write("## 5. Overall results\n\n")
    if overall:
        f.write("| Metric | Value |\n")
        f.write("|---|---:|\n")
        f.write(f"| Query count | {overall.get('query_count')} |\n")
        f.write(f"| MRR | {fmt(overall.get('MRR'))} |\n")
        f.write(f"| Precision@5 | {fmt(overall.get('precision_at_5'))} |\n")
        f.write(f"| Recall@5 | {fmt(overall.get('recall_at_5'))} |\n")
        f.write(f"| F1@5 | {fmt(overall.get('f1_at_5'))} |\n")
        f.write(f"| Same-family ratio@5 | {fmt(overall.get('same_family_ratio_at_5'))} |\n")
        f.write(f"| Cross-class contamination@5 | {fmt(overall.get('cross_class_contamination_at_5'))} |\n")
        f.write(f"| Self-hit ratio@5 | {fmt(overall.get('self_hit_ratio_at_5'))} |\n")
        f.write(f"| Benign/attack contamination@5 | {fmt(overall.get('benign_attack_contamination_at_5'))} |\n")
        f.write(f"| Evidence diversity@5 | {fmt(overall.get('evidence_diversity_at_5'))} |\n\n")

    f.write("## 6. Results by group\n\n")
    f.write("| Group | Queries | MRR | Precision@5 | Recall@5 | Contamination@5 | Self-hit@5 |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|\n")
    for r in summary:
        f.write(
            f"| {r.get('group')} | {r.get('query_count')} | {fmt(r.get('MRR'))} | "
            f"{fmt(r.get('precision_at_5'))} | {fmt(r.get('recall_at_5'))} | "
            f"{fmt(r.get('cross_class_contamination_at_5'))} | {fmt(r.get('self_hit_ratio_at_5'))} |\n"
        )
    f.write("\n")

    f.write("## 7. Weak queries and error analysis\n\n")
    if errors:
        f.write("The following queries were flagged because they had low Precision@5, low Recall@5, or high contamination:\n\n")
        f.write("| Query | Run | Type | Family | P@5 | R@5 | MRR | Contam@5 | Interpretation |\n")
        f.write("|---|---|---|---|---:|---:|---:|---:|---|\n")
        for r in errors:
            f.write(
                f"| {r['query_id']} | {r['run_id']} | {r['query_type']} | {r['expected_family']} | "
                f"{fmt(r['precision_at_5'])} | {fmt(r['recall_at_5'])} | {fmt(r['mrr'])} | "
                f"{fmt(r['cross_class_contamination_at_5'])} | {r['interpretation']} |\n"
            )
        f.write("\n")
    else:
        f.write("No weak queries were flagged under the current thresholds.\n\n")

    f.write("## 8. Interpretation\n\n")
    f.write("This phase makes the retriever visible and measurable. ")
    f.write("High Precision@k means the retriever gives mostly useful evidence. ")
    f.write("High Recall@k means the retriever finds a large portion of the known relevant evidence. ")
    f.write("High MRR means relevant evidence appears early in the ranking. ")
    f.write("High cross-class contamination means retrieved evidence may mislead the LLM by mixing attack families.\n\n")

    f.write("## 9. Research conclusion\n\n")
    f.write("Phase 10R provides the missing RAG validation layer requested by the supervisor. ")
    f.write("It separates retriever behavior from LLM reasoning and shows whether the RAG system is grounded in relevant evidence. ")
    f.write("The results should be used to justify Phase 10U, especially if contamination is high, recall is low, or the retriever depends too strongly on self-hit case documents.\n\n")

    f.write("## 10. Dashboard integration\n\n")
    f.write("The retriever evaluation is exported to dashboard-ready CSV files and displayed through a Streamlit dashboard page under `scripts/phase10E/pages/10_Retriever_Evaluation.py`.\n")

print("WROTE:", OUT)
