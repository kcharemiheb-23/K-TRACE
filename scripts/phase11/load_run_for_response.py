#!/usr/bin/env python3
"""Phase 11 - Load context for one run from existing project artifacts.

Returns a dict with: run_id, source (namespace/pod/intensity/...), and the path
to the enriched case file. The orchestrator uses this to seed the incident.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
LEDGER = ROOT / "artifacts/phase7/output/run-ledger.csv"
CASES = ROOT / "artifacts/phase10U/corpus_v2/cases"
P10D = ROOT / "artifacts/phase10D/results"

def load_run_context(run_id: str) -> dict:
    out = {
        "run_id": run_id,
        "source": {},
        "phase10u_case_path": "",
        "phase10d_result_path": "",
    }

    # 1. Phase 7 ledger row.
    if LEDGER.exists():
        with LEDGER.open(newline="") as f:
            for r in csv.DictReader(f):
                if r.get("run_id", "").strip() == run_id:
                    out["source"] = {
                        "namespace": r.get("source_namespace", "").strip() or "unknown",
                        "pod": r.get("source_pod", "").strip() or "unknown",
                        "target_scope": r.get("target_scope", "").strip() or "unknown",
                        "intensity": (r.get("intensity") or "").strip().lower() or "none",
                        "duration_sec": r.get("duration_sec", "").strip() or "0",
                        "scenario_family": r.get("scenario_family", "").strip(),
                        "subtype": r.get("subtype", "").strip(),
                    }
                    break

    # 2. Phase 10U enriched case file.
    case = CASES / f"{run_id}.md"
    if case.exists():
        out["phase10u_case_path"] = str(case)

    # 3. Phase 10D LLM result file.
    p10d = P10D / f"{run_id}.json"
    if p10d.exists():
        out["phase10d_result_path"] = str(p10d)

    return out

if __name__ == "__main__":
    import sys
    rid = sys.argv[1] if len(sys.argv) > 1 else "A3_LOW_002"
    print(json.dumps(load_run_context(rid), indent=2))
