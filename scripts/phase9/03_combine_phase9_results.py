#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

bin_path = ROOT / "artifacts" / "phase9" / "output" / "binary_best_model_summary.csv"
mul_path = ROOT / "artifacts" / "phase9" / "output" / "multiclass_best_model_summary.csv"
out_path = ROOT / "artifacts" / "phase9" / "output" / "phase9_combined_results.csv"

df = pd.concat([pd.read_csv(bin_path), pd.read_csv(mul_path)], axis=0).reset_index(drop=True)
df.to_csv(out_path, index=False)

print("WROTE:", out_path)
