#!/usr/bin/env python3
"""Phase 11 - Orchestrator. Run the full response pipeline for one run.

Usage:
  python3 scripts/phase11/run_response_pipeline.py --run_id A3_LOW_002 [--mode dry_run]

Modes: explain_only | dry_run | apply  (default dry_run)
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
P11 = ROOT / "scripts/phase11"
ART = ROOT / "artifacts/phase11"

INCIDENTS = ART / "incidents"
REPORTS = ART / "reports"
LOGS = ART / "logs"
SUMMARY = ART / "summary"
SUMMARY_CSV = SUMMARY / "phase11_run_summary.csv"
SKIPPED_CSV_FMT = LOGS / "skipped_benign_{day}.csv"

def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

loader   = _import("loader",   P11 / "load_run_for_response.py")
gate_mod = _import("gate",     P11 / "ml_attack_gate.py")
retr_mod = _import("retr",     P11 / "retrieve_response_context.py")
llm_mod  = _import("llm",      P11 / "generate_llm_response_report.py")
pol_mod  = _import("policy",   P11 / "select_remediation_action.py")
exe_mod  = _import("executor", P11 / "execute_or_dry_run_action.py")
rep_mod  = _import("reporter", P11 / "render_incident_report.py")

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _safe_id(s: str) -> str:
    return s.replace(":", "-").replace("Z", "")

def _ensure_dirs():
    for d in (INCIDENTS, REPORTS, LOGS, SUMMARY, ART / "actions"):
        d.mkdir(parents=True, exist_ok=True)

def _append_summary_row(row: dict):
    SUMMARY.mkdir(parents=True, exist_ok=True)
    fields = ["timestamp_utc","run_id","incident_id","gate_decision","family",
              "severity","action_id","mode","applied","manifest_path","report_md_path"]
    new = not SUMMARY_CSV.exists()
    with SUMMARY_CSV.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})

def _append_skipped(row: dict):
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    p = Path(str(SKIPPED_CSV_FMT).format(day=day))
    new = not p.exists()
    fields = ["timestamp_utc","run_id","binary_pred","multiclass_pred","family","reason"]
    with p.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})

def process_run(run_id: str, mode: str, top_k: int, log: logging.Logger) -> dict:
    ts = _now_iso()
    incident_id = f"INC_{_safe_id(ts)}_{run_id}"
    log.info("processing run %s (mode=%s)", run_id, mode)

    ctx = loader.load_run_context(run_id)
    gate = gate_mod.gate(run_id)

    if not gate.get("ok", False):
        log.error("gate failed for %s: %s", run_id, gate.get("error",""))
        _append_summary_row({
            "timestamp_utc": ts, "run_id": run_id, "incident_id": "",
            "gate_decision": "ERROR", "family": "",
            "severity": "", "action_id": "", "mode": mode,
            "applied": False, "manifest_path": "", "report_md_path": "",
        })
        return {"ok": False, "error": gate.get("error", "gate failed")}

    # BENIGN gate -> log skip and stop.
    if gate["gate_decision"] == "SKIP_BENIGN":
        log.info("BENIGN skip for %s", run_id)
        _append_skipped({
            "timestamp_utc": ts, "run_id": run_id,
            "binary_pred": gate["binary_pred"], "multiclass_pred": gate["multiclass_pred"],
            "family": gate["family"], "reason": "binary=BENIGN or family not in A1..A4",
        })
        _append_summary_row({
            "timestamp_utc": ts, "run_id": run_id, "incident_id": "",
            "gate_decision": "SKIP_BENIGN", "family": gate["family"],
            "severity": "LOW", "action_id": "NONE", "mode": mode,
            "applied": False, "manifest_path": "", "report_md_path": "",
        })
        return {"ok": True, "gate_decision": "SKIP_BENIGN", "run_id": run_id}

    # ATTACK path.
    incident = {
        "incident_id": incident_id,
        "run_id": run_id,
        "timestamp_utc": ts,
        "source": ctx.get("source", {}),
        "ml": gate,
    }

    incident["retrieval"] = retr_mod.retrieve_for_incident(
        run_id=run_id, predicted_family=gate["family"], top_k=top_k,
    )
    incident["llm"] = llm_mod.generate(
        run_id=run_id, family=gate["family"],
        source=incident["source"], retrieval=incident["retrieval"],
    )

    pol = pol_mod.select(
        family_label=gate["multiclass_pred"] or gate["family"],
        intensity=incident["source"].get("intensity", "medium"),
    )
    incident["policy"] = pol

    incident["remediation"] = exe_mod.execute(
        action_id=pol["action_id"], incident_id=incident_id, run_id=run_id,
        family=gate["family"], severity=pol["severity"],
        source=incident["source"], mode=mode,
    )

    json_path = INCIDENTS / f"{incident_id}.json"
    md_path = REPORTS / f"{incident_id}.md"
    incident["report"] = {"json_path": str(json_path), "md_path": str(md_path)}

    json_path.write_text(json.dumps(incident, indent=2))
    md_path.write_text(rep_mod.render(incident))

    _append_summary_row({
        "timestamp_utc": ts, "run_id": run_id, "incident_id": incident_id,
        "gate_decision": gate["gate_decision"], "family": gate["family"],
        "severity": pol["severity"], "action_id": pol["action_id"],
        "mode": mode, "applied": incident["remediation"]["applied"],
        "manifest_path": incident["remediation"].get("manifest_path", ""),
        "report_md_path": str(md_path),
    })

    log.info("incident saved: %s -> %s", incident_id, md_path)
    return {"ok": True, "gate_decision": "PASS_TO_RAG",
            "incident_id": incident_id, "run_id": run_id,
            "json_path": str(json_path), "md_path": str(md_path)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_id", required=True)
    ap.add_argument("--mode", default="dry_run", choices=["explain_only","dry_run","apply"])
    ap.add_argument("--top_k", default=5, type=int)
    args = ap.parse_args()

    _ensure_dirs()
    log_path = LOGS / f"orchestrator_run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )
    log = logging.getLogger("phase11")
    log.info("starting Phase 11 orchestrator run_id=%s mode=%s", args.run_id, args.mode)

    res = process_run(args.run_id, args.mode, args.top_k, log)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res.get("ok") else 1)

if __name__ == "__main__":
    main()
