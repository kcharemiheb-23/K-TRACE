#!/usr/bin/env python3
import csv
import json
import sys
from datetime import datetime, timezone
import matplotlib.pyplot as plt

def parse_z(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

if len(sys.argv) != 5:
    print("usage: plot_pilot_prom.py <run_id> <ledger_csv> <json_path> <out_png>")
    sys.exit(2)

run_id, ledger_csv, json_path, out_png = sys.argv[1:]

row = None
with open(ledger_csv) as f:
    for r in csv.DictReader(f):
        if r["run_id"] == run_id:
            row = r
            break

if row is None:
    raise SystemExit(f"run_id not found: {run_id}")

with open(json_path) as f:
    data = json.load(f)

series = data["data"]["result"]
if not series:
    raise SystemExit("no Prometheus series in JSON")

vals = series[0]["values"]
xs = [datetime.fromtimestamp(float(t), tz=timezone.utc) for t, _ in vals]
ys = [float(v) for _, v in vals]

raw_start = parse_z(row["raw_start_utc"])
raw_end = parse_z(row["raw_end_utc"])
eff_start = parse_z(row["effective_start_utc"])
eff_end = parse_z(row["effective_end_utc"])

plt.figure(figsize=(10, 4))
plt.plot(xs, ys)
plt.axvline(raw_start, linestyle="--")
plt.axvline(raw_end, linestyle="--")
plt.axvline(eff_start, linestyle=":")
plt.axvline(eff_end, linestyle=":")
plt.title(f"{run_id} signal")
plt.xlabel("UTC time")
plt.ylabel("value")
plt.tight_layout()
plt.savefig(out_png, dpi=200)
