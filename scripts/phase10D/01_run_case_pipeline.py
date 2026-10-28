#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

REASON = ROOT / "scripts" / "phase10D" / "03_reason_one_case.py"
REPORT = ROOT / "scripts" / "phase10D" / "04_write_case_report.py"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--top_k", type=int, default=4)
    args = parser.parse_args()

    subprocess.run([
        "python3", str(REASON),
        "--run_id", args.run_id,
        "--top_k", str(args.top_k)
    ], check=True)

    subprocess.run([
        "python3", str(REPORT),
        "--run_id", args.run_id
    ], check=True)

    print("PIPELINE COMPLETE FOR:", args.run_id)

if __name__ == "__main__":
    main()
