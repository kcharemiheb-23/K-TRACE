#!/usr/bin/env python3
import csv
import json
import os
import re
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

PLAN = ROOT / "scripts" / "phase7" / "plans" / "full_plan.csv"
RAW = ROOT / "artifacts" / "phase7" / "raw"
OUTDIR = ROOT / "artifacts" / "phase8" / "intermediate"

structured_envoy = OUTDIR / "structured_envoy.csv"
structured_falco = OUTDIR / "structured_falco.csv"
structured_prom = OUTDIR / "structured_prometheus.csv"

plan_rows = list(csv.DictReader(open(PLAN)))
plan_by_id = {r["run_id"]: r for r in plan_rows}

envoy_fields = [
    "run_id","class_label","scenario_family","subtype","intensity","benign_type",
    "source_file","source_pod","line_no","http_status","method","path_hint",
    "contains_4xx","contains_5xx","contains_trace","contains_options",
    "contains_script","contains_passwd","contains_sqlish"
]

falco_fields = [
    "run_id","class_label","scenario_family","subtype","intensity","benign_type",
    "source_file","source_pod","line_no","contains_falco","contains_proc",
    "contains_shell","contains_passwd","contains_nslookup","contains_whoami","contains_id"
]

prom_fields = [
    "run_id","class_label","scenario_family","subtype","intensity","benign_type",
    "source_file","metric_name","series_count","value_points"
]

status_re = re.compile(r'\s(\d{3})\s')
method_re = re.compile(r'"\s*(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE)\s+', re.IGNORECASE)

def truthy(s):
    return 1 if s else 0

with open(structured_envoy, "w", newline="") as fe, \
     open(structured_falco, "w", newline="") as ff, \
     open(structured_prom, "w", newline="") as fp:

    we = csv.DictWriter(fe, fieldnames=envoy_fields)
    wf = csv.DictWriter(ff, fieldnames=falco_fields)
    wp = csv.DictWriter(fp, fieldnames=prom_fields)

    we.writeheader()
    wf.writeheader()
    wp.writeheader()

    for rid, meta in plan_by_id.items():
        base = RAW / rid

        envoy_dir = base / "envoy"
        if envoy_dir.is_dir():
            for logf in sorted(envoy_dir.glob("*.log")):
                pod_name = logf.stem
                with open(logf, errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if not line.strip():
                            continue
                        m_status = status_re.search(line)
                        m_method = method_re.search(line)
                        http_status = m_status.group(1) if m_status else ""
                        method = m_method.group(1).upper() if m_method else ""
                        low = line.lower()
                        row = {
                            "run_id": rid,
                            "class_label": meta["class_label"],
                            "scenario_family": meta["scenario_family"],
                            "subtype": meta["subtype"],
                            "intensity": meta["intensity"],
                            "benign_type": meta["benign_type"],
                            "source_file": str(logf.relative_to(ROOT)),
                            "source_pod": pod_name,
                            "line_no": i,
                            "http_status": http_status,
                            "method": method,
                            "path_hint": line[:200].replace("\n"," "),
                            "contains_4xx": truthy(http_status.startswith("4")),
                            "contains_5xx": truthy(http_status.startswith("5")),
                            "contains_trace": truthy("trace" in low),
                            "contains_options": truthy("options" in low),
                            "contains_script": truthy("<script>" in low or "%3cscript" in low),
                            "contains_passwd": truthy("passwd" in low),
                            "contains_sqlish": truthy("or 1=1" in low or "%3d1" in low or "--" in low),
                        }
                        we.writerow(row)

        falco_dir = base / "falco"
        if falco_dir.is_dir():
            for logf in sorted(falco_dir.glob("*.log")):
                pod_name = logf.stem
                with open(logf, errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if not line.strip():
                            continue
                        low = line.lower()
                        row = {
                            "run_id": rid,
                            "class_label": meta["class_label"],
                            "scenario_family": meta["scenario_family"],
                            "subtype": meta["subtype"],
                            "intensity": meta["intensity"],
                            "benign_type": meta["benign_type"],
                            "source_file": str(logf.relative_to(ROOT)),
                            "source_pod": pod_name,
                            "line_no": i,
                            "contains_falco": truthy("falco" in low or "evt.type" in low or "rule=" in low),
                            "contains_proc": truthy("proc" in low or "execve" in low),
                            "contains_shell": truthy("sh" in low or "bash" in low),
                            "contains_passwd": truthy("passwd" in low),
                            "contains_nslookup": truthy("nslookup" in low),
                            "contains_whoami": truthy("whoami" in low),
                            "contains_id": truthy(" id" in low or low.strip().startswith("id")),
                        }
                        wf.writerow(row)

        prom_dir = base / "prometheus"
        if prom_dir.is_dir():
            for jf in sorted(prom_dir.glob("*.json")):
                metric_name = jf.stem
                try:
                    data = json.load(open(jf))
                    result = data.get("data", {}).get("result", [])
                    series_count = len(result)
                    value_points = 0
                    for s in result:
                        value_points += len(s.get("values", []))
                except Exception:
                    series_count = 0
                    value_points = 0

                row = {
                    "run_id": rid,
                    "class_label": meta["class_label"],
                    "scenario_family": meta["scenario_family"],
                    "subtype": meta["subtype"],
                    "intensity": meta["intensity"],
                    "benign_type": meta["benign_type"],
                    "source_file": str(jf.relative_to(ROOT)),
                    "metric_name": metric_name,
                    "series_count": series_count,
                    "value_points": value_points,
                }
                wp.writerow(row)

print("WROTE:", structured_envoy)
print("WROTE:", structured_falco)
print("WROTE:", structured_prom)
