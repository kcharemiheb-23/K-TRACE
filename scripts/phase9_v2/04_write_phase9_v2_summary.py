#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

bin_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "binary_best_model_summary_v2.csv").iloc[0].to_dict()
mul_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "multiclass_best_model_summary_v2.csv").iloc[0].to_dict()
rob = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "seed_robustness_results.csv")

out = ROOT / "artifacts" / "phase9_v2" / "reports" / "phase9_v2_summary.md"

with open(out, "w") as f:
    f.write("# Phase 9 v2 Summary\n\n")

    f.write("## Binary best model\n")
    for k, v in bin_sum.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n")

    f.write("## Multiclass best model\n")
    for k, v in mul_sum.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n")

    f.write("## Robustness note\n")
    for task in ["binary", "multiclass"]:
        sub = rob[rob["task"] == task]
        f.write(f"- {task}: mean accuracy={sub['accuracy'].mean():.4f}, std accuracy={sub['accuracy'].std():.4f}, mean f1_macro={sub['f1_macro'].mean():.4f}\n")
    f.write("\n")

    f.write("## Interpretation note\n")
    f.write("- Results are strong but still based on a small held-out test set.\n")
    f.write("- Binary and multiclass must be discussed separately.\n")
    f.write("- A3_RUNTIME_RECON should be discussed as the most difficult attack family if its per-class recall remains lower.\n")
    f.write("- Tree-based ensemble models should be presented as consistently strong, rather than overclaiming a single absolute winner.\n")

print("WROTE:", out)
