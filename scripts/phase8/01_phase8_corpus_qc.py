#!/usr/bin/env python3
import csv
import os
from collections import Counter, defaultdict
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

PLAN = ROOT / "scripts" / "phase7" / "plans" / "full_plan.csv"
MANIFEST = ROOT / "artifacts" / "phase7" / "output" / "dataset_run_manifest_clean.csv"
RAW = ROOT / "artifacts" / "phase7" / "raw"
REPORT = ROOT / "artifacts" / "phase8" / "reports" / "phase8_qc_report.md"

def nonempty_dir(path):
    return path.is_dir() and any(True for _ in os.scandir(path))

plan_rows = list(csv.DictReader(open(PLAN)))
manifest_rows = list(csv.DictReader(open(MANIFEST)))

plan_ids = {r["run_id"] for r in plan_rows}
manifest_ids = {r["run_id"] for r in manifest_rows}
raw_ids = {d.name for d in RAW.iterdir() if d.is_dir()}

valid = []
invalid = []
missing = []

for r in plan_rows:
    rid = r["run_id"]
    p = RAW / rid
    if not p.is_dir():
        missing.append(rid)
        continue

    envoy_ok = nonempty_dir(p / "envoy")
    falco_ok = nonempty_dir(p / "falco")
    prom_ok = nonempty_dir(p / "prometheus")

    if envoy_ok and falco_ok and prom_ok:
        valid.append(rid)
    else:
        invalid.append(rid)

class_counts = Counter(r["class_label"] for r in plan_rows)
family_counts = Counter(r["scenario_family"] for r in plan_rows)
trim_counts = defaultdict(set)
for r in plan_rows:
    trim_counts[r["class_label"]].add((r["trim_start_sec"], r["trim_end_sec"]))

extra_raw = sorted(raw_ids - plan_ids)

with open(REPORT, "w") as f:
    f.write("# Phase 8 QC Report\n\n")
    f.write("## Corpus completeness\n")
    f.write(f"- planned runs: {len(plan_rows)}\n")
    f.write(f"- manifest runs: {len(manifest_rows)}\n")
    f.write(f"- valid official runs: {len(valid)}\n")
    f.write(f"- invalid official runs: {len(invalid)}\n")
    f.write(f"- missing official runs: {len(missing)}\n")
    f.write(f"- extra raw dirs: {len(extra_raw)}\n\n")

    f.write("## Scenario family counts\n")
    for k, v in sorted(family_counts.items()):
        f.write(f"- {k}: {v}\n")
    f.write("\n")

    f.write("## Class counts\n")
    for k, v in sorted(class_counts.items()):
        f.write(f"- {k}: {v}\n")
    f.write("\n")

    f.write("## Trim policy by class\n")
    for k in sorted(trim_counts):
        f.write(f"- {k}: {sorted(trim_counts[k])}\n")
    f.write("\n")

    f.write("## Extra raw dirs\n")
    for x in extra_raw:
        f.write(f"- {x}\n")
    f.write("\n")

    f.write("## Invalid official runs\n")
    for x in invalid:
        f.write(f"- {x}\n")
    f.write("\n")

    f.write("## Missing official runs\n")
    for x in missing:
        f.write(f"- {x}\n")
    f.write("\n")

print("WROTE:", REPORT)
print("VALID_OFFICIAL_RUNS:", len(valid))
print("INVALID_OFFICIAL_RUNS:", len(invalid))
print("MISSING_OFFICIAL_RUNS:", len(missing))
