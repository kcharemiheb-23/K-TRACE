#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUT = ROOT / "artifacts" / "phase9" / "reports" / "phase9_experiment_manifest.md"

paths = {
    "binary": ROOT / "artifacts" / "phase8" / "output" / "feature_dataset_binary.csv",
    "multiclass": ROOT / "artifacts" / "phase8" / "output" / "feature_dataset_multiclass.csv",
    "train": ROOT / "artifacts" / "phase8" / "output" / "split_train_runs.csv",
    "val": ROOT / "artifacts" / "phase8" / "output" / "split_val_runs.csv",
    "test": ROOT / "artifacts" / "phase8" / "output" / "split_test_runs.csv",
}

def read_csv(path):
    return list(csv.DictReader(open(path)))

binary_rows = read_csv(paths["binary"])
multi_rows = read_csv(paths["multiclass"])
train_rows = read_csv(paths["train"])
val_rows = read_csv(paths["val"])
test_rows = read_csv(paths["test"])

with open(OUT, "w") as f:
    f.write("# Phase 9 Experiment Manifest\n\n")
    f.write("## Dataset files\n")
    for k, v in paths.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n")

    f.write("## Counts\n")
    f.write(f"- binary rows: {len(binary_rows)}\n")
    f.write(f"- multiclass rows: {len(multi_rows)}\n")
    f.write(f"- train rows: {len(train_rows)}\n")
    f.write(f"- val rows: {len(val_rows)}\n")
    f.write(f"- test rows: {len(test_rows)}\n")
    f.write(f"- binary feature columns: {len(binary_rows[0].keys())}\n")
    f.write(f"- multiclass feature columns: {len(multi_rows[0].keys())}\n")
    f.write("\n")

    f.write("## Class distributions\n")
    f.write(f"- binary: {Counter(r['binary_label'] for r in binary_rows)}\n")
    f.write(f"- multiclass: {Counter(r['class_label'] for r in multi_rows)}\n")
    f.write(f"- train: {Counter(r['class_label'] for r in train_rows)}\n")
    f.write(f"- val: {Counter(r['class_label'] for r in val_rows)}\n")
    f.write(f"- test: {Counter(r['class_label'] for r in test_rows)}\n")
    f.write("\n")

    f.write("## Seed\n")
    f.write("- random_state: 42\n")

print("WROTE:", OUT)
