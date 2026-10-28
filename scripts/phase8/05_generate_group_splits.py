#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path
import random

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC = ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv"
OUTDIR = ROOT / "artifacts" / "phase8" / "output"

rows = list(csv.DictReader(open(SRC)))

by_class = defaultdict(list)
for r in rows:
    by_class[r["class_label"]].append(r)

rng = random.Random(42)

train = []
val = []
test = []

for cls, items in by_class.items():
    items = list(items)
    rng.shuffle(items)

    n = len(items)
    n_train = max(1, int(round(n * 0.6)))
    n_val = max(1, int(round(n * 0.2)))
    n_test = n - n_train - n_val

    if n_test < 1:
        n_test = 1
        if n_train > n_val:
            n_train -= 1
        else:
            n_val -= 1

    train.extend(items[:n_train])
    val.extend(items[n_train:n_train+n_val])
    test.extend(items[n_train+n_val:])

def write_rows(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

write_rows(OUTDIR / "split_train_runs.csv", train)
write_rows(OUTDIR / "split_val_runs.csv", val)
write_rows(OUTDIR / "split_test_runs.csv", test)

print("TRAIN:", len(train))
print("VAL:", len(val))
print("TEST:", len(test))
