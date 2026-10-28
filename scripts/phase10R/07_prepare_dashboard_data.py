#!/usr/bin/env python3
from pathlib import Path
import shutil
import json
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC_FILES = {
    "retrieval_metrics_summary.csv": ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_summary.csv",
    "retrieval_metrics_by_query.csv": ROOT / "artifacts" / "phase10R" / "output" / "retrieval_metrics_by_query.csv",
    "retrieval_ranked_results.csv": ROOT / "artifacts" / "phase10R" / "output" / "retrieval_ranked_results.csv",
    "retrieval_error_analysis.csv": ROOT / "artifacts" / "phase10R" / "output" / "retrieval_error_analysis.csv",
    "retriever_ground_truth.csv": ROOT / "artifacts" / "phase10R" / "scoring" / "retriever_ground_truth.csv",
}

DASH = ROOT / "artifacts" / "phase10R" / "dashboard"
REPORT = ROOT / "artifacts" / "phase10R" / "reports" / "phase10R_retriever_evaluation_report.md"
SUMMARY_JSON = DASH / "phase10R_dashboard_summary.json"

DASH.mkdir(parents=True, exist_ok=True)

for name, src in SRC_FILES.items():
    if src.exists():
        dst = DASH / name
        shutil.copy2(src, dst)
        print("COPIED:", dst)
    else:
        print("MISSING:", src)

summary_csv = DASH / "retrieval_metrics_summary.csv"
overall = {}
if summary_csv.exists():
    rows = list(csv.DictReader(open(summary_csv, newline="", encoding="utf-8")))
    for r in rows:
        if r.get("group") == "ALL":
            overall = r
            break

payload = {
    "phase": "phase10R",
    "title": "Retriever Inspection, Ground Truth, SMART Metrics, and Dashboard Integration",
    "approach": "Dense semantic vector retrieval using Chroma and embedding-based top-k ranking",
    "not_bm25": True,
    "not_exact_keyword": True,
    "overall": overall,
    "report_path": str(REPORT),
}

with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print("WROTE:", SUMMARY_JSON)
