#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

bin_path = ROOT / "artifacts" / "phase9_v2" / "output" / "binary_best_model_summary_v2.csv"
mul_path = ROOT / "artifacts" / "phase9_v2" / "output" / "multiclass_best_model_summary_v2.csv"
out = ROOT / "artifacts" / "phase9_v2" / "output" / "phase9_v2_combined_results.csv"

df = pd.concat([pd.read_csv(bin_path), pd.read_csv(mul_path)], axis=0).reset_index(drop=True)
df.to_csv(out, index=False)
print("WROTE:", out)
