#!/usr/bin/env python3
import csv
import pathlib
import re
import sys

if len(sys.argv) != 4:
    print("usage: extract_falco_pilot_window.py <run_id> <raw_dir> <out_csv>", file=sys.stderr)
    sys.exit(2)

run_id = sys.argv[1]
raw_dir = pathlib.Path(sys.argv[2])
out_csv = pathlib.Path(sys.argv[3])

# Falco logs often begin with ISO-like timestamps or contain them near start
ts_re = re.compile(r'(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)')

rows = []
for log_file in sorted(raw_dir.glob("*.log")):
    try:
        with log_file.open(errors="ignore") as f:
            for line in f:
                m = ts_re.search(line)
                if not m:
                    continue
                ts = m.group("ts")
                rows.append((ts, log_file.name))
    except Exception:
        pass

rows.sort()

with out_csv.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["run_id", "timestamp_utc", "source_file"])
    for ts, src in rows:
        w.writerow([run_id, ts, src])

print(f"[OK] wrote {out_csv} rows={len(rows)}")
