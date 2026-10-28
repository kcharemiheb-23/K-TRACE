#!/usr/bin/env python3
import csv
from collections import Counter, defaultdict
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

PLAN = ROOT / "scripts" / "phase7" / "plans" / "full_plan.csv"
ENV = ROOT / "artifacts" / "phase8" / "intermediate" / "structured_envoy.csv"
FAL = ROOT / "artifacts" / "phase8" / "intermediate" / "structured_falco.csv"
PRO = ROOT / "artifacts" / "phase8" / "intermediate" / "structured_prometheus.csv"

OUT = ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv"

plan_rows = list(csv.DictReader(open(PLAN)))
meta = {r["run_id"]: r for r in plan_rows}

env_stats = defaultdict(Counter)
fal_stats = defaultdict(Counter)
pro_stats = defaultdict(Counter)

with open(ENV) as f:
    for r in csv.DictReader(f):
        rid = r["run_id"]
        env_stats[rid]["envoy_lines"] += 1
        env_stats[rid]["status_4xx"] += int(r["contains_4xx"])
        env_stats[rid]["status_5xx"] += int(r["contains_5xx"])
        env_stats[rid]["method_trace"] += int(r["contains_trace"])
        env_stats[rid]["method_options"] += int(r["contains_options"])
        env_stats[rid]["payload_script"] += int(r["contains_script"])
        env_stats[rid]["payload_passwd"] += int(r["contains_passwd"])
        env_stats[rid]["payload_sqlish"] += int(r["contains_sqlish"])
        if r["method"]:
            env_stats[rid][f"method_{r['method']}"] += 1
        if r["source_pod"]:
            env_stats[rid][f"pod_{r['source_pod']}"] += 1

with open(FAL) as f:
    for r in csv.DictReader(f):
        rid = r["run_id"]
        fal_stats[rid]["falco_lines"] += 1
        fal_stats[rid]["falco_proc"] += int(r["contains_proc"])
        fal_stats[rid]["falco_shell"] += int(r["contains_shell"])
        fal_stats[rid]["falco_passwd"] += int(r["contains_passwd"])
        fal_stats[rid]["falco_nslookup"] += int(r["contains_nslookup"])
        fal_stats[rid]["falco_whoami"] += int(r["contains_whoami"])
        fal_stats[rid]["falco_id"] += int(r["contains_id"])

with open(PRO) as f:
    for r in csv.DictReader(f):
        rid = r["run_id"]
        metric = r["metric_name"]
        pro_stats[rid][f"prom_series_{metric}"] += int(r["series_count"])
        pro_stats[rid][f"prom_points_{metric}"] += int(r["value_points"])

all_keys = set()
for d in [env_stats, fal_stats, pro_stats]:
    for rid in d:
        all_keys.update(d[rid].keys())

fieldnames = [
    "run_id","class_label","scenario_family","subtype","intensity","benign_type",
    "binary_label"
] + sorted(all_keys)

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()

    for rid, m in meta.items():
        row = {
            "run_id": rid,
            "class_label": m["class_label"],
            "scenario_family": m["scenario_family"],
            "subtype": m["subtype"],
            "intensity": m["intensity"],
            "benign_type": m["benign_type"],
            "binary_label": "ATTACK" if m["scenario_family"] == "ATTACK" else "BENIGN"
        }
        for k in all_keys:
            row[k] = 0

        for k, v in env_stats[rid].items():
            row[k] = v
        for k, v in fal_stats[rid].items():
            row[k] = v
        for k, v in pro_stats[rid].items():
            row[k] = v

        w.writerow(row)

print("WROTE:", OUT)
