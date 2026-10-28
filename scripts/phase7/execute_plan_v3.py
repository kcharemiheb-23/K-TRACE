#!/usr/bin/env python3
import csv
import datetime as dt
import pathlib
import subprocess
import sys
import time

HOME = pathlib.Path.home()
ROOT = HOME / "cloud-native-ids-azure"
RAW_ROOT = ROOT / "artifacts" / "phase7" / "raw"
OUT_ROOT = ROOT / "artifacts" / "phase7" / "output"
LEDGER = OUT_ROOT / "run-ledger.csv"

COLLECT_ENVOY = ROOT / "scripts" / "phase7" / "collect_envoy_raw.sh"
COLLECT_FALCO = ROOT / "scripts" / "phase7" / "collect_falco_raw.sh"
COLLECT_PROM = ROOT / "scripts" / "phase7" / "collect_prometheus_raw.sh"

GAP_SEC = 25

def utc_now():
    return dt.datetime.now(dt.timezone.utc)

def iso_z(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

def run_cmd(cmd, cwd=None):
    return subprocess.run(cmd, shell=True, executable="/bin/bash", cwd=cwd, text=True, capture_output=True)

def append_ledger(row):
    with LEDGER.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "run_id","class_label","scenario_family","subtype","intensity","benign_type",
            "source_namespace","source_pod","target_scope","duration_sec",
            "trim_start_sec","trim_end_sec","raw_start_utc","raw_end_utc",
            "effective_start_utc","effective_end_utc","status","payload_cmd"
        ])
        writer.writerow(row)

def main(plan_csv):
    with open(plan_csv) as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        run_id = row["run_id"]
        run_dir = RAW_ROOT / run_id / "runner"
        run_dir.mkdir(parents=True, exist_ok=True)

        raw_start = utc_now()
        result = run_cmd(row["payload_cmd"])
        raw_end = utc_now()

        trim_start = int(row["trim_start_sec"])
        trim_end = int(row["trim_end_sec"])

        effective_start = raw_start + dt.timedelta(seconds=trim_start)
        effective_end = raw_end - dt.timedelta(seconds=trim_end)

        status = result.returncode
        if effective_end <= effective_start:
            status = 3

        (run_dir / "stdout.txt").write_text(result.stdout)
        (run_dir / "stderr.txt").write_text(result.stderr)

        ledger_row = {
            "run_id": row["run_id"],
            "class_label": row["class_label"],
            "scenario_family": row["scenario_family"],
            "subtype": row["subtype"],
            "intensity": row["intensity"],
            "benign_type": row["benign_type"],
            "source_namespace": row["source_namespace"],
            "source_pod": row["source_pod"],
            "target_scope": row["target_scope"],
            "duration_sec": row["duration_sec"],
            "trim_start_sec": row["trim_start_sec"],
            "trim_end_sec": row["trim_end_sec"],
            "raw_start_utc": iso_z(raw_start),
            "raw_end_utc": iso_z(raw_end),
            "effective_start_utc": iso_z(effective_start),
            "effective_end_utc": iso_z(effective_end),
            "status": str(status),
            "payload_cmd": row["payload_cmd"],
        }
        append_ledger(ledger_row)

        print(f"[INFO] {run_id} status={status}")

        if status == 0:
            subprocess.run(f'bash "{COLLECT_ENVOY}" "{run_id}" "{iso_z(raw_start)}"', shell=True, executable="/bin/bash", check=False)
            subprocess.run(f'bash "{COLLECT_FALCO}" "{run_id}" "{iso_z(raw_start)}"', shell=True, executable="/bin/bash", check=False)
            subprocess.run(f'bash "{COLLECT_PROM}" "{run_id}" "{iso_z(raw_start)}" "{iso_z(raw_end)}"', shell=True, executable="/bin/bash", check=False)
        else:
            print(f"[WARN] skipping collectors for failed run {run_id}")

        print(f"[INFO] cooldown {GAP_SEC}s")
        time.sleep(GAP_SEC)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: execute_plan_v3.py <plan_csv>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
