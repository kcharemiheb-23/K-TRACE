#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUT = ROOT / "artifacts" / "phase10A" / "reports" / "phase10A_source_manifest.md"

paths = {
    "phase8_run_feature_dataset": ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv",
    "phase8_split_test_runs": ROOT / "artifacts" / "phase8" / "output" / "split_test_runs.csv",
    "phase9_log": ROOT / "docs" / "phase-logs" / "phase9.md",
    "phase9_v2_log": ROOT / "docs" / "phase-logs" / "phase9_v2.md",
    "phase9_v2_binary_summary": ROOT / "artifacts" / "phase9_v2" / "output" / "binary_best_model_summary_v2.csv",
    "phase9_v2_multiclass_summary": ROOT / "artifacts" / "phase9_v2" / "output" / "multiclass_best_model_summary_v2.csv",
    "phase9_v2_combined_results": ROOT / "artifacts" / "phase9_v2" / "output" / "phase9_v2_combined_results.csv",
    "phase9_v2_seed_robustness": ROOT / "artifacts" / "phase9_v2" / "output" / "seed_robustness_results.csv",
    "phase9_v2_binary_report": ROOT / "artifacts" / "phase9_v2" / "reports" / "binary_best_model_test_report_v2.txt",
    "phase9_v2_multiclass_report": ROOT / "artifacts" / "phase9_v2" / "reports" / "multiclass_best_model_test_report_v2.txt",
    "phase9_v2_summary_report": ROOT / "artifacts" / "phase9_v2" / "reports" / "phase9_v2_summary.md",
    "phase9_v2_supervisor_report": ROOT / "artifacts" / "phase9_v2" / "reports" / "phase9_supervisor_summary.md",
}

def csv_rows(path):
    try:
        with open(path, "r", newline="") as f:
            return sum(1 for _ in f) - 1
    except Exception:
        return "n/a"

with open(OUT, "w") as f:
    f.write("# Phase 10A Source Manifest\n\n")
    f.write("## Purpose\n")
    f.write("This manifest records the exact environment artifacts reused to build the Phase 10A RAG corpus.\n\n")
    f.write("## Inputs\n")
    for name, path in paths.items():
        exists = path.exists()
        f.write(f"- {name}: {path} | exists={exists}")
        if exists and path.suffix == ".csv":
            f.write(f" | data_rows={csv_rows(path)}")
        f.write("\n")

print("WROTE:", OUT)
