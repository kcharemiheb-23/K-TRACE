#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

bin_sum = pd.read_csv(ROOT / "artifacts" / "phase9" / "output" / "binary_best_model_summary.csv")
mul_sum = pd.read_csv(ROOT / "artifacts" / "phase9" / "output" / "multiclass_best_model_summary.csv")
out = ROOT / "artifacts" / "phase9" / "reports" / "phase9_summary.md"

b = bin_sum.iloc[0].to_dict()
m = mul_sum.iloc[0].to_dict()

with open(out, "w") as f:
    f.write("# Phase 9 Summary\n\n")
    f.write("## Binary task\n")
    for k, v in b.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n")
    f.write("## Multiclass task\n")
    for k, v in m.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n")
    f.write("## Interpretation note\n")
    f.write("- Results must be interpreted using the leakage-safe run-based split policy from Phase 8.\n")
    f.write("- Binary and multiclass results should be discussed separately.\n")
    f.write("- Feature importance plots should be used to explain source contribution.\n")

print("WROTE:", out)
