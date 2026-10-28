#!/usr/bin/env python3
"""Phase 11 - ML attack gate.

Reads the multiclass prediction recorded in the enriched Phase 10U case file
(preserved from the Phase 9 v2 RandomForest model). Decides BENIGN vs ATTACK
and returns the predicted attack family.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
CASES = ROOT / "artifacts/phase10U/corpus_v2/cases"

BIN_RE = re.compile(r"-\s*Binary predicted label:\s*(\S+)")
MULTI_RE = re.compile(r"-\s*Multiclass predicted label:\s*(\S+)")
BIN_TRUE_RE = re.compile(r"-\s*Binary true label:\s*(\S+)")
MULTI_TRUE_RE = re.compile(r"-\s*Multiclass true label:\s*(\S+)")

def family_of(label: str) -> str:
    label = (label or "").upper()
    if label.startswith("BENIGN"):
        return "BENIGN"
    for f in ("A1", "A2", "A3", "A4"):
        if label.startswith(f):
            return f
    return "UNKNOWN"

def gate(run_id: str) -> dict:
    case = CASES / f"{run_id}.md"
    if not case.exists():
        return {
            "ok": False,
            "error": f"enriched case not found at {case}",
        }
    text = case.read_text()
    bin_pred = (BIN_RE.search(text).group(1) if BIN_RE.search(text) else "").upper()
    multi_pred = (MULTI_RE.search(text).group(1) if MULTI_RE.search(text) else "").upper()
    bin_true = (BIN_TRUE_RE.search(text).group(1) if BIN_TRUE_RE.search(text) else "").upper()
    multi_true = (MULTI_TRUE_RE.search(text).group(1) if MULTI_TRUE_RE.search(text) else "").upper()

    fam = family_of(multi_pred)
    is_attack = bin_pred == "ATTACK" and fam in {"A1", "A2", "A3", "A4"}

    return {
        "ok": True,
        "binary_model": "DecisionTree",
        "multiclass_model": "RandomForest",
        "binary_pred": bin_pred or "UNKNOWN",
        "multiclass_pred": multi_pred or "UNKNOWN",
        "binary_true": bin_true,
        "multiclass_true": multi_true,
        "family": fam,
        "gate_decision": "PASS_TO_RAG" if is_attack else "SKIP_BENIGN",
    }

if __name__ == "__main__":
    import sys
    rid = sys.argv[1] if len(sys.argv) > 1 else "A3_LOW_002"
    print(json.dumps(gate(rid), indent=2))
