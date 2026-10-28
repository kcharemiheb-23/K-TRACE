#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUTDIR = ROOT / "artifacts" / "phase10A" / "corpus" / "ml_results"

bin_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "binary_best_model_summary_v2.csv").iloc[0].to_dict()
mul_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "multiclass_best_model_summary_v2.csv").iloc[0].to_dict()
combined = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "phase9_v2_combined_results.csv")
rob = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "seed_robustness_results.csv")

binary_report = (ROOT / "artifacts" / "phase9_v2" / "reports" / "binary_best_model_test_report_v2.txt").read_text()
multiclass_report = (ROOT / "artifacts" / "phase9_v2" / "reports" / "multiclass_best_model_test_report_v2.txt").read_text()

with open(OUTDIR / "binary_best_model.md", "w") as f:
    f.write("# Binary Best Model\n\n")
    for k, v in bin_sum.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n## Test report\n\n```text\n")
    f.write(binary_report)
    f.write("\n```\n")

with open(OUTDIR / "multiclass_best_model.md", "w") as f:
    f.write("# Multiclass Best Model\n\n")
    for k, v in mul_sum.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n## Test report\n\n```text\n")
    f.write(multiclass_report)
    f.write("\n```\n")

with open(OUTDIR / "combined_results.md", "w") as f:
    f.write("# Combined Phase 9 v2 Results\n\n")
    f.write(combined.to_markdown(index=False))
    f.write("\n")

with open(OUTDIR / "robustness.md", "w") as f:
    f.write("# Seed Robustness Results\n\n")
    for task in ["binary", "multiclass"]:
        sub = rob[rob["task"] == task]
        f.write(f"## {task}\n")
        f.write(f"- mean_accuracy: {sub['accuracy'].mean():.4f}\n")
        f.write(f"- std_accuracy: {sub['accuracy'].std():.4f}\n")
        f.write(f"- mean_f1_macro: {sub['f1_macro'].mean():.4f}\n\n")
        f.write(sub.to_markdown(index=False))
        f.write("\n\n")

print("WROTE ML result docs in", OUTDIR)
