#!/usr/bin/env python3
from pathlib import Path
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
RESULTS = ROOT / "artifacts" / "phase10D" / "results"
OUT = ROOT / "artifacts" / "phase10D" / "reports" / "phase10D_summary.md"

files = sorted(RESULTS.glob("*.json"))

with open(OUT, "w") as f:
    f.write("# Phase 10D Summary\n\n")
    f.write("## Goal\n")
    f.write("Integrate the validated RAG backend and best local LLM into a standardized offline IDS reasoning system.\n\n")

    f.write("## Produced case results\n")
    for p in files:
        f.write(f"- {p.name}\n")
    f.write("\n")

    f.write("## Result snapshots\n")
    for p in files:
        data = json.loads(p.read_text())
        f.write(f"### {data['run_id']}\n")
        f.write(f"- class_label: {data['class_label']}\n")
        f.write(f"- binary_pred_label: {data['binary_pred_label']}\n")
        f.write(f"- multiclass_pred_label: {data['multiclass_pred_label']}\n")
        f.write(f"- llm_decision: {data['llm_decision']}\n")
        f.write(f"- llm_model: {data['llm_model']}\n\n")

print("WROTE:", OUT)
