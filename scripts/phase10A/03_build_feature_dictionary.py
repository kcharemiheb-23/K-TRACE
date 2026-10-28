#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
SRC = ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv"
OUT = ROOT / "artifacts" / "phase10A" / "corpus" / "features" / "feature_dictionary.md"
CSVOUT = ROOT / "artifacts" / "phase10A" / "output" / "feature_groups.csv"

META_COLS = ["run_id","class_label","scenario_family","subtype","intensity","benign_type","binary_label"]

with open(SRC, "r", newline="") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

features = [h for h in headers if h not in META_COLS]

groups = {"Envoy": [], "Falco": [], "Prometheus": [], "Other": []}
for feat in features:
    if feat.startswith("envoy_") or feat.startswith("status_") or feat.startswith("method_") or feat.startswith("payload_") or feat.startswith("pod_"):
        groups["Envoy"].append(feat)
    elif feat.startswith("falco_"):
        groups["Falco"].append(feat)
    elif feat.startswith("prom_"):
        groups["Prometheus"].append(feat)
    else:
        groups["Other"].append(feat)

with open(OUT, "w") as f:
    f.write("# Feature Dictionary\n\n")
    f.write("This document is built directly from the Phase 8 run-level dataset header.\n\n")
    f.write(f"- total feature columns: {len(features)}\n\n")
    for group, cols in groups.items():
        f.write(f"## {group}\n")
        f.write(f"- count: {len(cols)}\n")
        for c in cols:
            f.write(f"- `{c}`\n")
        f.write("\n")

with open(CSVOUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["group", "feature_name"])
    for group, cols in groups.items():
        for c in cols:
            writer.writerow([group, c])

print("WROTE:", OUT)
print("WROTE:", CSVOUT)
