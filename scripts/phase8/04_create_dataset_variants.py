#!/usr/bin/env python3
import csv
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC = ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv"
BIN = ROOT / "artifacts" / "phase8" / "output" / "feature_dataset_binary.csv"
MUL = ROOT / "artifacts" / "phase8" / "output" / "feature_dataset_multiclass.csv"

rows = list(csv.DictReader(open(SRC)))
fieldnames = rows[0].keys()

with open(BIN, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

with open(MUL, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print("WROTE:", BIN)
print("WROTE:", MUL)
print("ROWS:", len(rows))
