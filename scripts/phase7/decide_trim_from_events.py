#!/usr/bin/env python3
import csv
import datetime as dt
import sys

if len(sys.argv) != 5:
    print("usage: decide_trim_from_events.py <run_id> <ledger_csv> <event_csv> <out_txt>", file=sys.stderr)
    sys.exit(2)

run_id, ledger_csv, event_csv, out_txt = sys.argv[1:]

ledger_row = None
with open(ledger_csv) as f:
    for row in csv.DictReader(f):
        if row["run_id"] == run_id:
            ledger_row = row
            break

if ledger_row is None:
    raise SystemExit(f"run_id not found: {run_id}")

def parse_z(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)

raw_start = parse_z(ledger_row["raw_start_utc"])
raw_end = parse_z(ledger_row["raw_end_utc"])

events = []
with open(event_csv) as f:
    for row in csv.DictReader(f):
        ts = row["timestamp_utc"]
        try:
            if "." in ts:
                t = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)
            else:
                t = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            events.append(t)
        except Exception:
            pass

events.sort()

if not events:
    first = None
    last = None
    trim_start = None
    trim_end = None
else:
    first = events[0]
    last = events[-1]
    trim_start = max(0, int((first - raw_start).total_seconds()))
    trim_end = max(0, int((raw_end - last).total_seconds()))

with open(out_txt, "w") as f:
    f.write(f"run_id={run_id}\n")
    f.write(f"raw_start_utc={ledger_row['raw_start_utc']}\n")
    f.write(f"raw_end_utc={ledger_row['raw_end_utc']}\n")
    f.write(f"first_event_utc={first.isoformat().replace('+00:00','Z') if first else 'NONE'}\n")
    f.write(f"last_event_utc={last.isoformat().replace('+00:00','Z') if last else 'NONE'}\n")
    f.write(f"suggested_trim_start_sec={trim_start if trim_start is not None else 'NONE'}\n")
    f.write(f"suggested_trim_end_sec={trim_end if trim_end is not None else 'NONE'}\n")
